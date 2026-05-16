import base64
import hashlib
import hmac
import json

from pydantic import SecretStr

from virtualme.config import Settings
from virtualme.responder.core import ResponderResult
from virtualme.transport import responder_line


class FakeRequest:
    def __init__(self, body: bytes, signature: str):
        self._body = body
        self.headers = {"x-line-signature": signature}

    async def body(self):
        return self._body


def _settings() -> Settings:
    return Settings(
        anthropic_api_key=SecretStr("test"),
        responder_line_channel_secret=SecretStr("secret"),
        responder_line_channel_access_token=SecretStr("token"),
    )


def _line_body(text: str = "hello", reply_token: str | None = "reply-token") -> bytes:
    event = {
        "type": "message",
        "mode": "active",
        "timestamp": 1,
        "webhookEventId": "01FZ74A0TDDPYRVKNK77XKC3ZR",
        "deliveryContext": {"isRedelivery": False},
        "source": {"type": "user", "userId": "U123"},
        "message": {"id": "m1", "type": "text", "text": text, "quoteToken": "quote-token"},
    }
    if reply_token is not None:
        event["replyToken"] = reply_token
    return json.dumps({"destination": "bot", "events": [event]}).encode()


def _signature(body: bytes) -> str:
    digest = hmac.new(b"secret", body, hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


def _patch_line_api(monkeypatch, sent):
    class FakeApiClient:
        def __init__(self, configuration):
            self.configuration = configuration

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

    class FakeMessagingApi:
        def __init__(self, api_client):
            self.api_client = api_client

        async def reply_message(self, request):
            sent.append(("reply", request.reply_token, request.messages[0].text))

        async def push_message(self, request):
            sent.append(("push", request.to, request.messages[0].text))

    monkeypatch.setattr(responder_line, "AsyncApiClient", FakeApiClient)
    monkeypatch.setattr(responder_line, "AsyncMessagingApi", FakeMessagingApi)


async def test_valid_text_event_calls_respond_and_reply(monkeypatch):
    body = _line_body()
    sent = []

    async def fake_respond(incoming_message, persona_context, claude, settings):
        assert incoming_message == "hello"
        assert persona_context == "persona context"
        return ResponderResult(reply="reply", is_liability=False)

    monkeypatch.setattr(responder_line, "respond", fake_respond)
    _patch_line_api(monkeypatch, sent)

    result = await responder_line.handle_responder_webhook(
        FakeRequest(body, _signature(body)),
        object(),
        _settings().responder_line_channel_secret,
        _settings().responder_line_channel_access_token,
        "persona context",
        None,
        _settings(),
    )

    assert result == {"status": "ok", "handled": 1}
    assert sent == [("reply", "reply-token", "reply")]


async def test_liability_message_pushes_owner_notice(monkeypatch):
    body = _line_body("想問資遣費怎麼算")
    sent = []

    async def fake_respond(incoming_message, persona_context, claude, settings):
        assert incoming_message == "想問資遣費怎麼算"
        return ResponderResult(reply="資遣費回覆", is_liability=True)

    monkeypatch.setattr(responder_line, "respond", fake_respond)
    _patch_line_api(monkeypatch, sent)

    result = await responder_line.handle_responder_webhook(
        FakeRequest(body, _signature(body)),
        object(),
        _settings().responder_line_channel_secret,
        _settings().responder_line_channel_access_token,
        "persona context",
        "UOWNER",
        _settings(),
    )

    assert result == {"status": "ok", "handled": 1}
    assert sent[0] == ("reply", "reply-token", "資遣費回覆")
    assert sent[1][0] == "push"
    assert sent[1][1] == "UOWNER"
    assert "【AI 助理轉達｜涉及權責】" in sent[1][2]  # noqa: RUF001
    assert "對方提問：想問資遣費怎麼算" in sent[1][2]  # noqa: RUF001
    assert "AI 回覆：資遣費回覆" in sent[1][2]  # noqa: RUF001
    assert "請你確認。" in sent[1][2]


async def test_missing_persona_returns_clear_error():
    body = _line_body()
    result = await responder_line.handle_responder_webhook(
        FakeRequest(body, _signature(body)),
        object(),
        _settings().responder_line_channel_secret,
        _settings().responder_line_channel_access_token,
        "",
        None,
        _settings(),
    )

    assert result == {"status": "missing_persona"}


async def test_missing_credentials_returns_clear_error():
    settings = Settings(anthropic_api_key=SecretStr("test"))
    body = _line_body()
    result = await responder_line.handle_responder_webhook(
        FakeRequest(body, _signature(body)),
        object(),
        settings.responder_line_channel_secret,
        settings.responder_line_channel_access_token,
        "persona context",
        None,
        settings,
    )

    assert result == {"status": "missing_responder_credentials"}
