"""Fetch ALL currently live TfL JamCam IDs and print their names."""

import httpx

r = httpx.get("https://api.tfl.gov.uk/Place/Type/JamCam")
cams = r.json()
print(f"Total live JamCams: {len(cams)}\n")

# Sort by commonName for readability and print first 30
cams.sort(key=lambda c: c["commonName"])
for c in cams[:50]:
    print(f"  {c['id']:30s}  {c['commonName']}")
