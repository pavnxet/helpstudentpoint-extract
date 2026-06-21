import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

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


HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HelpStudentPoint-Extract/1.0)"}


def fetch_listing():
    resp = requests.get(BASE_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


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


def download_file(url, dest):
    resp = requests.get(url, headers=HEADERS, stream=True, timeout=120)
    resp.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)


def main():
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    manifest = load_manifest()

    print("Fetching directory listing...")
    html = fetch_listing()
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
            download_file(f["url"], dest)
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
