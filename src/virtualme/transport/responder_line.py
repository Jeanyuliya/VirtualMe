import logging
from typing import Any

from anthropic import AsyncAnthropic
from fastapi import Request
from linebot.v3 import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    PushMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from virtualme.config import Settings
from virtualme.responder.core import respond
from virtualme.transport.line import _send_reply_or_push

logger = logging.getLogger(__name__)

RESPONDER_ERROR_REPLY = "抱歉, AI 助理暫時無法回覆。請稍後再試, 或直接向本人確認。"


async def handle_responder_webhook(
    request: Request,
    claude: AsyncAnthropic,
    secret,
    access_token,
    persona_context: str | None,
    owner_user_id: str | None,
    settings: Settings,
) -> dict[str, Any]:
    secret_value = _secret_value(secret)
    access_token_value = _secret_value(access_token)
    if not secret_value or not access_token_value:
        logger.error("Responder LINE webhook called without channel credentials")
        return {"status": "missing_responder_credentials"}
    if not persona_context:
        logger.error("Responder LINE webhook called without persona context")
        return {"status": "missing_persona"}

    body = await request.body()
    signature = request.headers.get("x-line-signature", "")
    parser = WebhookParser(secret_value)
    try:
        events = parser.parse(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        logger.warning("Responder LINE webhook rejected due to invalid signature")
        return {"status": "invalid_signature"}
    except Exception as exc:
        logger.warning("Responder LINE webhook rejected due to malformed signature or body: %s", exc)
        return {"status": "invalid_signature"}

    configuration = Configuration(access_token=access_token_value)
    handled = 0
    async with AsyncApiClient(configuration) as api_client:
        line_bot_api = AsyncMessagingApi(api_client)
        for event in events:
            if not isinstance(event, MessageEvent):
                continue
            if not isinstance(event.message, TextMessageContent):
                continue
            if not event.reply_token:
                logger.warning("Responder LINE text event skipped because reply_token is missing")
                continue

            user_id = getattr(event.source, "user_id", None)
            if not user_id:
                logger.warning("Responder LINE text event skipped because user_id is missing")
                continue

            incoming_message = event.message.text
            try:
                result = await respond(incoming_message, persona_context, claude, settings)
                reply = result.reply
                is_liability = result.is_liability
            except Exception as exc:
                logger.error("Responder respond failed for %s: %s", user_id, exc)
                reply = RESPONDER_ERROR_REPLY
                is_liability = False

            if await _send_reply_or_push(line_bot_api, event.reply_token, user_id, reply):
                handled += 1

            if is_liability and owner_user_id:
                await _push_owner_liability_notice(
                    line_bot_api,
                    owner_user_id,
                    incoming_message,
                    reply,
                )

    return {"status": "ok", "handled": handled}


async def _push_owner_liability_notice(
    line_bot_api: AsyncMessagingApi,
    owner_user_id: str,
    incoming_message: str,
    reply: str,
) -> None:
    text = (
        "【AI 助理轉達｜涉及權責】\n"  # noqa: RUF001
        f"對方提問：{incoming_message}\n"  # noqa: RUF001
        f"AI 回覆：{reply}\n"  # noqa: RUF001
        "請你確認。"
    )
    try:
        await line_bot_api.push_message(
            PushMessageRequest(to=owner_user_id, messages=[TextMessage(text=text)])
        )
        logger.info("Responder liability notice pushed to owner %s", owner_user_id)
    except Exception as exc:
        logger.error("Responder liability owner push failed for %s: %s", owner_user_id, exc)


def _secret_value(secret) -> str | None:
    return secret.get_secret_value() if hasattr(secret, "get_secret_value") else secret
