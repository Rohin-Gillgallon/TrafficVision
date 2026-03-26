import asyncio
import asyncpg


async def add_canary_wharf():
    conn = await asyncpg.connect("postgresql://user:pass@localhost:5433/trafficcv")
    await conn.execute(
        "INSERT INTO cameras (id, tfl_id, name, rsu_id, x, y, lat, lon) "
        "VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
        "canary-wharf",
        "JamCams_00002.00390",
        "Canary Wharf / Westferry",
        "RSU-00390",
        0.0,
        0.0,
        51.5049,
        -0.0215,
    )
    count = await conn.fetchval("SELECT count(*) FROM cameras")
    print(f"✅ Canary Wharf added. Total cameras: {count}")
    await conn.close()


if __name__ == "__main__":
    asyncio.run(add_canary_wharf())
