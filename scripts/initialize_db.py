import asyncio
import httpx
from sqlalchemy import select
from src.db.crud import init_db, create_camera, get_session
from src.db.models import Camera

# Verified, strictly deterministic live high-traffic IDs
STATIC_CAMERAS = [
    {
        "id": "a4-cromwell",
        "name": "A4 Cromwell Rd / Queens Gate",
        "tfl_id": "JamCams_00001.06607",
    },
    {
        "id": "a40-western-ave",
        "name": "A40 Western Ave / West End Rd",
        "tfl_id": "JamCams_00001.07318",
    },
    {
        "id": "a406-billet",
        "name": "A406 Billet Upass E",
        "tfl_id": "JamCams_00002.00865",
    },
    {
        "id": "marylebone-rd",
        "name": "Marylebone Rd / York Gate",
        "tfl_id": "JamCams_00001.07367",
    },
    {
        "id": "hyde-park-corner",
        "name": "Hyde Park Corner / Park Lane",
        "tfl_id": "JamCams_00001.08750",
    },
    {
        "id": "euston-rd",
        "name": "Euston Rd / Conway St",
        "tfl_id": "JamCams_00001.07387",
    },
    {
        "id": "tower-bridge-app",
        "name": "Tower Bridge App. / East Smithfield",
        "tfl_id": "JamCams_00001.03500",
    },
    {
        "id": "westminster-bridge-rd",
        "name": "Baylis Rd / Westminster Bridge Rd",
        "tfl_id": "JamCams_00001.06510",
    },
    {
        "id": "waterloo-bridge",
        "name": "Waterloo Bridge South",
        "tfl_id": "JamCams_00001.04223",
    },
    {
        "id": "oxford-st",
        "name": "Oxford St / Orchard St",
        "tfl_id": "JamCams_00001.08858",
    },
]


async def seed_cameras():
    print("3/3 🌍 Fetching live camera coordinates from TfL...")
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.tfl.gov.uk/Place/Type/JamCam")
        all_cams = resp.json()

    cam_map = {c["id"]: c for c in all_cams}

    for spec in STATIC_CAMERAS:
        cam_data = cam_map.get(spec["tfl_id"])
        if not cam_data:
            print(
                f"⚠️ Warning: Could not find live API data for {spec['name']} ({spec['tfl_id']})"
            )
            continue

        await create_camera(
            camera_id=spec["id"],
            tfl_id=spec["tfl_id"],
            name=spec["name"],
            rsu_id=f"RSU-{spec['tfl_id'].split('.')[-1]}",
            x=0.0,
            y=0.0,
            lat=cam_data["lat"],
            lon=cam_data["lon"],
        )
        print(f"  ✅ Registered: {spec['name']:40s} ({spec['tfl_id']})")


async def main():
    print("1/3 ⏳ Waiting for database to be ready...")
    max_retries = 10
    initialized = False

    for i in range(max_retries):
        try:
            await init_db()
            print("2/3 ✅ Database connected and schema initialized successfully!")
            initialized = True
            break
        except Exception:
            print(
                f"  ⚠️ Attempt {i+1}/{max_retries} failed (database starting up). Retrying in 3 seconds..."
            )
            await asyncio.sleep(3)

    if not initialized:
        print("❌ Failed to connect to database.")
        return

    # Seed cameras
    await seed_cameras()

    # Verify
    async with get_session() as session:
        res = await session.execute(select(Camera))
        count = len(res.scalars().all())
    print(f"\n✨ Initialization complete! Database now has {count} active cameras.")


if __name__ == "__main__":
    asyncio.run(main())
