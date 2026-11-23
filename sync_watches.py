import json
import os
import urllib.request
import urllib.error

API_URL = "https://watch-api-eight.vercel.app"
SNAPSHOT_ENDPOINT = f"{API_URL}/api/v1/watches/snapshot"

# Optional relative paths to your other two frontend folders if stored nearby
TARGET_PATHS = [
    "watches.json",
    "../chronicle/watches.json",
    "../broke-oclock/watches.json",
]

def sync_watches_json():
    print(f"Fetching latest snapshot from {SNAPSHOT_ENDPOINT}...")
    req = urllib.request.Request(
        SNAPSHOT_ENDPOINT,
        headers={"User-Agent": "WatchGallerySync/1.0"}
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as err:
        print(f"Failed to fetch snapshot: {err}")
        return

    formatted_json = json.dumps(payload, indent=2, ensure_ascii=False)

    for path in TARGET_PATHS:
        parent_dir = os.path.dirname(path)
        if not parent_dir or os.path.isdir(parent_dir):
            with open(path, "w", encoding="utf-8") as f:
                f.write(formatted_json + "\n")
            print(f"Saved {payload.get('count', 0)} watches ({payload.get('version')}) -> {path}")

if __name__ == "__main__":
    sync_watches_json()