import asyncio
import asyncpg


async def check():
    conn = await asyncpg.connect("postgresql://user:pass@localhost:5433/trafficcv")
    rows = await conn.fetch("SELECT id, name, tfl_id FROM cameras ORDER BY id")
    print(f"Total cameras in DB: {len(rows)}")
    for r in rows:
        print(
            f"  {r['id']:25s} | {r['name'] or 'NO NAME':35s} | {r['tfl_id'] or 'NO TFL_ID'}"
        )

    det_count = await conn.fetchval("SELECT count(*) FROM detections")
    print(f"\nTotal detections: {det_count}")
    await conn.close()


if __name__ == "__main__":
    asyncio.run(check())
