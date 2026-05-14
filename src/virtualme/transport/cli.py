import asyncio

from anthropic import AsyncAnthropic

from virtualme.config import Settings, sqlite_path
from virtualme.interview.bot import process_turn
from virtualme.interview.question_selector import QuestionSelector, load_question_pool
from virtualme.storage.db import DB


def _selector() -> QuestionSelector:
    return QuestionSelector(load_question_pool())


async def main() -> None:
    settings = Settings()
    db = DB(sqlite_path(settings.database_url))
    claude = AsyncAnthropic(api_key=settings.anthropic_api_key.get_secret_value())
    selector = _selector()
    interviewee_id = "local"
    print("VirtualMe CLI. Ctrl-D to exit.")
    while True:
        try:
            incoming = input("> ").strip()
        except EOFError:
            break
        if not incoming:
            continue
        reply = await process_turn(interviewee_id, incoming, claude, db, selector, settings)
        print(reply)


if __name__ == "__main__":
    asyncio.run(main())
