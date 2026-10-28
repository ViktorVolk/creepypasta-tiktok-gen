import asyncio
import sys
from src.pipeline import CreepypastaPipeline


async def main():
    if len(sys.argv) > 1:
        topic = sys.argv[1]
    else:
        topic = None

    pipeline = CreepypastaPipeline()
    await pipeline.run(topic)


if __name__ == "__main__":
    asyncio.run(main())
