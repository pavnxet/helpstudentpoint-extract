# HelpStudentPoint Extractor

Automatically extracts PDFs and images from [file.helpstudentpoint.com](https://file.helpstudentpoint.com/wp-content/uploads/2026/06/) every 6 hours and deploys a searchable gallery via GitHub Pages.

## How It Works

1. **GitHub Actions** runs every 6 hours (or manually)
2. Parses the directory listing on the source website
3. Downloads any new PDFs/images not yet in the repo
4. Commits them to the `downloads/` folder
5. Deploys the liquid glass UI to **GitHub Pages**

## Setup (One-time)

### 1. Enable GitHub Pages

Go to your repo **Settings → Pages**:

- **Source**: Select **GitHub Actions** (not "Deploy from a branch")
- This allows the workflow to deploy directly

### 2. Enable the Workflow

Go to **Actions** tab:

- Click **"I understand my workflows, go ahead and enable them"**
- The extract workflow will now run every 6 hours automatically

### 3. (Optional) Manual Trigger

Go to **Actions → Extract & Deploy → Run workflow** to trigger it immediately.

## Project Structure

```
├── .github/workflows/extract.yml   # GitHub Actions: extract + deploy
├── css/liquid-glass.css            # Liquid glass design system
├── js/app.js                       # Search, filter, dynamic file listing
├── index.html                      # Main page (aurora glass UI)
├── scripts/extract.py              # Python scraper
├── downloaded.json                 # Tracks what's been downloaded
├── downloads/                      # Extracted PDFs & images
└── requirements.txt
```

## Tech Stack

- **Backend**: Python (requests + BeautifulSoup4)
- **Frontend**: Vanilla HTML/CSS/JS with Liquid Glass design system
- **CI/CD**: GitHub Actions (cron + manual trigger)
- **Hosting**: GitHub Pages

## Local Development

```bash
pip install -r requirements.txt
python scripts/extract.py
```

Then open `index.html` in a browser (note: `downloaded.json` must exist with file entries for the UI to show content).

## License

MIT
