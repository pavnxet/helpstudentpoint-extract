import os
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote
from bs4 import BeautifulSoup

try:
    from curl_cffi import requests as cffi_requests
    def fetch_html(url):
        r = cffi_requests.get(url, impersonate="chrome", timeout=30)
        r.raise_for_status()
        return r.text
    def download_bytes(url):
        r = cffi_requests.get(url, impersonate="chrome", timeout=120)
        r.raise_for_status()
        return r.content
except ImportError:
    import urllib.request, ssl
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    def fetch_html(url):
        req = urllib.request.Request(url, headers=HEADERS)
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            return resp.read().decode("utf-8", errors="replace")
    def download_bytes(url):
        req = urllib.request.Request(url, headers=HEADERS)
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
            return resp.read()

BASE_URL = "https://file.helpstudentpoint.com/wp-content/uploads/2026/06/"
DOWNLOAD_DIR = Path("downloads")
MANIFEST_PATH = Path("downloaded.json")
EXTENSIONS = {".pdf", ".jpeg", ".jpg", ".png"}


def load_manifest():
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {}


def save_manifest(manifest):
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def parse_files(html):
    soup = BeautifulSoup(html, "html.parser")
    files = []
    for row in soup.select("tr"):
        link = row.select_one("td a")
        if not link:
            continue
        href = link.get("href", "")
        name = unquote(href.split("/")[-1])
        ext = Path(name).suffix.lower()
        if ext not in EXTENSIONS:
            continue
        cells = row.select("td")
        last_modified = cells[1].text.strip() if len(cells) > 1 else ""
        size_text = cells[2].text.strip() if len(cells) > 2 else ""
        files.append({
            "name": name,
            "url": BASE_URL + unquote(href.split("/")[-1]),
            "last_modified": last_modified,
            "size": size_text,
        })
    return files


def main():
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    manifest = load_manifest()

    print("Fetching directory listing...")
    html = fetch_html(BASE_URL)
    files = parse_files(html)
    print(f"Found {len(files)} eligible files on server")

    new_files = [f for f in files if f["name"] not in manifest]
    print(f"New files to download: {len(new_files)}")

    if not new_files:
        print("Nothing new. Done.")
        return

    for f in new_files:
        dest = DOWNLOAD_DIR / f["name"]
        print(f"  Downloading: {f['name']} ({f['size']}) ...")
        try:
            data = download_bytes(f["url"])
            dest.write_bytes(data)
            manifest[f["name"]] = {
                "url": f["url"],
                "last_modified": f["last_modified"],
                "size": f["size"],
                "downloaded_at": datetime.now(timezone.utc).isoformat(),
            }
            print(f"    OK")
        except Exception as e:
            print(f"    FAILED: {e}")

    save_manifest(manifest)
    print(f"Manifest updated. Total tracked: {len(manifest)}")


if __name__ == "__main__":
    main()
