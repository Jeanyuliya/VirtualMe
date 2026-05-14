import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from virtualme.storage.db import init_db


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default="./data/virtualme.db")
    args = parser.parse_args()
    await init_db(args.path)
    print(f"initialized {args.path}")


if __name__ == "__main__":
    asyncio.run(main())
