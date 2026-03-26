import asyncio
from sqlalchemy import text
from src.db.crud import engine


async def add_column():
    async with engine.begin() as conn:
        print("Checking if image_url column exists...")
        await conn.execute(
            text("ALTER TABLE detections ADD COLUMN IF NOT EXISTS image_url VARCHAR")
        )
        print("Done.")


if __name__ == "__main__":
    asyncio.run(add_column())
