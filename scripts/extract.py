import json
import re
import urllib.request
import ssl
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

BASE_URL = "https://file.helpstudentpoint.com/wp-content/uploads/2026/06/"
JINA_URL = "https://r.jina.ai/" + BASE_URL
MANIFEST_PATH = Path("downloaded.json")
EXTENSIONS = {".pdf", ".jpeg", ".jpg", ".png"}


def load_manifest():
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {}


def save_manifest(manifest):
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def fetch_listing():
    req = urllib.request.Request(JINA_URL, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/plain",
    })
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_files(text):
    files = []
    pattern = re.compile(r'\[.*?\]\((https://file\.helpstudentpoint\.com/wp-content/uploads/2026/06/[^)]+)\)')
    for match in pattern.finditer(text):
        url = match.group(1)
        name = unquote(url.split("/")[-1])
        ext = Path(name).suffix.lower()
        if ext not in EXTENSIONS:
            continue
        files.append({
            "name": name,
            "url": url,
        })
    return files


def main():
    manifest = load_manifest()

    print("Fetching directory listing via Jina Reader...")
    text = fetch_listing()
    files = parse_files(text)
    print(f"Found {len(files)} eligible files on server")

    new_files = [f for f in files if f["name"] not in manifest]
    print(f"New files: {len(new_files)}")

    if not new_files:
        print("Nothing new. Done.")
        return

    for f in new_files:
        manifest[f["name"]] = {
            "url": f["url"],
            "downloaded_at": datetime.now(timezone.utc).isoformat(),
        }
        print(f"  + {f['name']}")

    save_manifest(manifest)
    print(f"Manifest updated. Total tracked: {len(manifest)}")


if __name__ == "__main__":
    main()
