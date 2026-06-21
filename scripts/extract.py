import json
import os
import re
import urllib.request
import ssl
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, quote

BASE_URL = "https://file.helpstudentpoint.com/wp-content/uploads/2026/06/"
JINA_URL = "https://r.jina.ai/" + BASE_URL
MANIFEST_PATH = Path("downloaded.json")
DOWNLOAD_DIR = Path("downloads")
EXTENSIONS = {".pdf", ".jpeg", ".jpg", ".png"}
PROXY_URL = os.environ.get("PROXY_URL", "")


def load_manifest():
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {}


def save_manifest(manifest):
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def fetch_url(url):
    ctx = ssl.create_default_context()
    if PROXY_URL:
        proxy_url = f"{PROXY_URL}?url={quote(url, safe='')}"
        req = urllib.request.Request(proxy_url, headers={"User-Agent": "Mozilla/5.0"})
    else:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
        return resp.read()


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
    DOWNLOAD_DIR.mkdir(exist_ok=True)
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
        dest = DOWNLOAD_DIR / f["name"]
        print(f"  + {f['name']} ...", end=" ")
        try:
            data = fetch_url(f["url"])
            dest.write_bytes(data)
            print(f"OK ({len(data)} bytes)")
            manifest[f["name"]] = {
                "url": f["url"],
                "downloaded_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            print(f"FAILED: {e}")
            manifest[f["name"]] = {
                "url": f["url"],
                "downloaded_at": datetime.now(timezone.utc).isoformat(),
                "download_error": str(e),
            }

    save_manifest(manifest)
    print(f"Manifest updated. Total tracked: {len(manifest)}")


if __name__ == "__main__":
    main()
