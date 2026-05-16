import logging
from contextlib import asynccontextmanager

from anthropic import AsyncAnthropic
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request

from virtualme import __version__
from virtualme.config import Settings, sqlite_path
from virtualme.interview.question_selector import QuestionSelector, load_question_pool
from virtualme.responder.persona import load_persona
from virtualme.storage.db import DB
from virtualme.transport.line import handle_line_webhook
from virtualme.transport.responder_line import handle_responder_webhook

logger = logging.getLogger(__name__)

settings = Settings()
db = DB(sqlite_path(settings.database_url))
claude = AsyncAnthropic(api_key=settings.anthropic_api_key.get_secret_value(), max_retries=4)
selector = QuestionSelector(load_question_pool())
try:
    responder_persona = (
        load_persona(settings.persona_archive_dir) if settings.persona_archive_dir else None
    )
except FileNotFoundError as exc:
    logger.warning("Responder persona archive could not be loaded: %s", exc)
    responder_persona = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await db.init()
    yield


app = FastAPI(title="VirtualMe", version=__version__, lifespan=lifespan)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"ok": "true", "version": __version__}


@app.post("/webhook/line")
async def line_webhook(request: Request, background_tasks: BackgroundTasks) -> dict:
    secret = (
        settings.line_channel_secret.get_secret_value()
        if settings.line_channel_secret is not None
        else None
    )
    result = await handle_line_webhook(
        request,
        claude,
        db,
        selector,
        secret,
        settings,
        background_tasks,
    )
    if result.get("status") == "invalid_signature":
        raise HTTPException(status_code=400, detail="invalid LINE signature")
    if result.get("status") == "missing_line_credentials":
        raise HTTPException(status_code=503, detail="LINE credentials are not configured")
    return result


@app.post("/webhook/responder")
async def responder_webhook(request: Request) -> dict:
    result = await handle_responder_webhook(
        request,
        claude,
        settings.responder_line_channel_secret,
        settings.responder_line_channel_access_token,
        responder_persona,
        settings.owner_line_user_id,
        settings,
    )
    if result.get("status") == "invalid_signature":
        raise HTTPException(status_code=400, detail="invalid responder LINE signature")
    if result.get("status") == "missing_responder_credentials":
        raise HTTPException(status_code=503, detail="Responder LINE credentials are not configured")
    if result.get("status") == "missing_persona":
        raise HTTPException(status_code=503, detail="Responder persona is not configured")
    return result
