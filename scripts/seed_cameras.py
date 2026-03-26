import asyncio
import httpx
from src.db.crud import AsyncSessionLocal, init_db
from src.db.models import Camera, Detection
from sqlalchemy import delete

# slugs as ID, display name, and TfL JamCam ID
STATIC_CAMERAS = [
    {
        "id": "piccadilly-circus",
        "name": "Piccadilly Circus",
        "tfl_id": "JamCams_00001.03150",
    },
    {
        "id": "old-street",
        "name": "Old Street / City Road",
        "tfl_id": "JamCams_00001.07632",
    },
    {
        "id": "elephant-and-castle",
        "name": "Elephant and Castle",
        "tfl_id": "JamCams_00001.02528",
    },
    {
        "id": "kings-cross",
        "name": "Euston Road / King's Cross",
        "tfl_id": "JamCams_00001.06551",
    },
    {"id": "vauxhall-cross", "name": "Vauxhall Cross", "tfl_id": "JamCams_00001.04250"},
    {
        "id": "hanger-lane",
        "name": "Hanger Lane Gyratory",
        "tfl_id": "JamCams_00001.06010",
    },
    {
        "id": "bow-interchange",
        "name": "Bow Interchange",
        "tfl_id": "JamCams_00001.06606",
    },
    {"id": "hyde-park", "name": "Hyde Park Corner", "tfl_id": "JamCams_00001.07005"},
    {
        "id": "shepherds-bush",
        "name": "Shepherds Bush Green",
        "tfl_id": "JamCams_00001.07701",
    },
    {
        "id": "canary-wharf",
        "name": "Canary Wharf / Limehouse Link",
        "tfl_id": "JamCams_00001.12501",
    },
]


async def seed_static_cameras():
    print("🏗️ Initializing database...")
    await init_db()

    # 1. Fetch live data from TfL for coordinates
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.tfl.gov.uk/Place/Type/JamCam")
        all_cams = resp.json()
    cam_map = {c["id"]: c for c in all_cams}

    async with AsyncSessionLocal() as session:
        # 2. Cleanup
        print("🧹 Cleaning up old data...")
        await session.execute(delete(Detection))
        await session.execute(delete(Camera))

        # 3. Seed
        print(f"🚀 Seeding {len(STATIC_CAMERAS)} high-traffic nodes...")
        for spec in STATIC_CAMERAS:
            c = cam_map.get(spec["tfl_id"])
            if not c:
                print(f"⚠️ Warning: {spec['tfl_id']} not found in TfL live data.")
                continue

            cam = Camera(
                id=spec["id"],
                tfl_id=spec["tfl_id"],
                name=spec["name"],
                rsu_id=f"RSU-{spec['tfl_id'].split('.')[-1]}",
                x=0.0,
                y=0.0,
                lat=c["lat"],
                lon=c["lon"],
            )
            session.add(cam)
            print(f"✅ Prepped: {spec['name']}")

        await session.commit()
    print("✨ Seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_static_cameras())
