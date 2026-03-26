"""
Auto-discover 10 real, high-traffic JamCams from the live TfL API and seed them.
Drops and recreates tables to ensure a clean schema.
"""

import asyncio
import asyncpg
import httpx

DATABASE_DSN = "postgresql://user:pass@localhost:5433/trafficcv"

# Keywords to search for in camera commonName — these are major London junctions
WANTED_KEYWORDS = [
    "A4 Cromwell",
    "A40 Western Ave",
    "A2 Old Kent",
    "A406",
    "Marylebone Rd",
    "Park Lane",
    "Euston Rd",
    "Blackwall Tnl",
    "Tower Bridge",
    "Vauxhall Bridge",
    "Westminster Bridge",
    "Waterloo Bridge",
    "Oxford St",
    "Strand",
    "Victoria Embankment",
    "Kings Cross",
    "Old Street",
    "Elephant",
    "Piccadilly",
    "Shepherds Bush",
]


def slug(name: str) -> str:
    """Turn a camera name into a URL-friendly slug."""
    return name.lower().replace(" ", "-").replace("/", "-").replace(".", "")[:40]


async def main():
    # 1. Fetch all live cameras
    print("1/3  Fetching live TfL JamCam list...")
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.tfl.gov.uk/Place/Type/JamCam")
        all_cams = resp.json()
    print(f"     Found {len(all_cams)} live cameras.")

    # 2. Pick 10 by matching keywords to commonName
    picked = []
    used_keywords = set()
    for kw in WANTED_KEYWORDS:
        if len(picked) >= 10:
            break
        kw_lower = kw.lower()
        for cam in all_cams:
            if kw_lower in cam["commonName"].lower() and cam["id"] not in {
                p["tfl_id"] for p in picked
            }:
                picked.append(
                    {
                        "tfl_id": cam["id"],
                        "name": cam["commonName"],
                        "lat": cam["lat"],
                        "lon": cam["lon"],
                    }
                )
                used_keywords.add(kw)
                break  # one per keyword

    if len(picked) < 10:
        # Fill remaining with whatever is available
        for cam in all_cams:
            if len(picked) >= 10:
                break
            if cam["id"] not in {p["tfl_id"] for p in picked}:
                picked.append(
                    {
                        "tfl_id": cam["id"],
                        "name": cam["commonName"],
                        "lat": cam["lat"],
                        "lon": cam["lon"],
                    }
                )

    # Generate slug IDs
    for p in picked:
        p["id"] = slug(p["name"])

    # 3. Seed database
    print("2/3  Dropping old tables and creating fresh schema...")
    conn = await asyncpg.connect(DATABASE_DSN)
    await conn.execute("DROP TABLE IF EXISTS detections CASCADE")
    await conn.execute("DROP TABLE IF EXISTS cameras CASCADE")
    await conn.execute(
        """
        CREATE TABLE cameras (
            id       TEXT PRIMARY KEY,
            tfl_id   VARCHAR(100),
            name     VARCHAR(200),
            rsu_id   VARCHAR(100) NOT NULL,
            x        DOUBLE PRECISION NOT NULL,
            y        DOUBLE PRECISION NOT NULL,
            lat      DOUBLE PRECISION NOT NULL,
            lon      DOUBLE PRECISION NOT NULL,
            simtime  DOUBLE PRECISION
        )
    """
    )
    await conn.execute(
        """
        CREATE TABLE detections (
            id             TEXT PRIMARY KEY,
            camera_id      TEXT NOT NULL,
            lat            DOUBLE PRECISION NOT NULL,
            lon            DOUBLE PRECISION NOT NULL,
            detected_at    TIMESTAMP DEFAULT now(),
            vehicle_class  TEXT NOT NULL,
            confidence     DOUBLE PRECISION NOT NULL,
            bbox           JSONB NOT NULL,
            frame_key      TEXT,
            image_url      TEXT,
            simtime        DOUBLE PRECISION
        )
    """
    )
    await conn.execute("CREATE INDEX ix_det_cam ON detections (camera_id)")
    await conn.execute("CREATE INDEX ix_det_dat ON detections (detected_at)")
    await conn.execute("CREATE INDEX ix_cam_tfl ON cameras (tfl_id)")

    print("3/3  Seeding 10 verified high-traffic nodes...")
    for p in picked:
        await conn.execute(
            "INSERT INTO cameras (id, tfl_id, name, rsu_id, x, y, lat, lon) "
            "VALUES ($1,$2,$3,$4,$5,$6,$7,$8)",
            p["id"],
            p["tfl_id"],
            p["name"],
            f"RSU-{p['tfl_id'].split('.')[-1]}",
            0.0,
            0.0,
            p["lat"],
            p["lon"],
        )
        print(f"  ✅  {p['name']:40s}  ({p['tfl_id']})")

    count = await conn.fetchval("SELECT count(*) FROM cameras")
    print(f"\n✨  Done! {count} cameras registered.")
    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
