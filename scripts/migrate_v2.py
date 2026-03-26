import asyncio
from sqlalchemy import text
from src.db.crud import engine


async def migrate():
    async with engine.begin() as conn:
        print("Creating cameras table if not exists...")
        await conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS cameras (
                id VARCHAR PRIMARY KEY,
                rsu_id VARCHAR(100) NOT NULL,
                x FLOAT NOT NULL,
                y FLOAT NOT NULL,
                lat FLOAT NOT NULL,
                lon FLOAT NOT NULL,
                simtime FLOAT
            )
        """
            )
        )

        print("Adding columns to detections table...")
        columns = [("simtime", "FLOAT")]
        for col, type in columns:
            try:
                await conn.execute(
                    text(
                        f"ALTER TABLE detections ADD COLUMN IF NOT EXISTS {col} {type}"
                    )
                )
            except Exception as e:
                print(f"Column {col} might already exist: {e}")

        print("Migration complete.")


if __name__ == "__main__":
    asyncio.run(migrate())
