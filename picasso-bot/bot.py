import os
import random
import tempfile
import requests
from bs4 import BeautifulSoup
from mastodon import Mastodon

# ── Config (set these as GitHub Actions secrets) ─────────────────────────────
MASTODON_BASE_URL    = os.environ["MASTODON_BASE_URL"]     # e.g. https://mastodon.social
MASTODON_ACCESS_TOKEN = os.environ["MASTODON_ACCESS_TOKEN"]

TARGET_URL = "https://www.artchive.com/paintings-by-artist/pablo-picasso/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

# ── Scraper ───────────────────────────────────────────────────────────────────

def fetch_paintings():
    """Scrape the Picasso page and return a list of painting dicts."""
    resp = requests.get(TARGET_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    paintings = []
    seen_urls = set()

    for a in soup.find_all("a", href=True):
        img = a.find("img")
        if not img:
            continue

        src = img.get("src") or img.get("data-src") or img.get("data-lazy-src") or ""
        if not src or any(x in src for x in ("logo", "icon", "placeholder", "avatar")):
            continue

        img_url = src if src.startswith("http") else "https://www.artchive.com" + src
        if img_url in seen_urls:
            continue
        seen_urls.add(img_url)

        # Title: heading inside parent container, then alt text
        title = ""
        parent = a.find_parent(["div", "article", "li", "figure"])
        if parent:
            heading = parent.find(["h1","h2","h3","h4","h5"])
            if heading:
                title = heading.get_text(strip=True)
        if not title:
            title = img.get("alt") or img.get("title") or "Untitled"

        # Year: first 4-digit year in surrounding text
        year = ""
        container_text = (parent or a.parent).get_text(" ") if (parent or a.parent) else ""
        import re
        m = re.search(r"\b(1[89]\d{2}|20[012]\d)\b", container_text)
        if m:
            year = m.group(0)

        paintings.append({"title": title, "year": year, "img_url": img_url})

    if not paintings:
        raise RuntimeError("No paintings found — the site structure may have changed.")

    return paintings


def download_image(url: str) -> str:
    """Download image to a temp file, return the file path."""
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    content_type = resp.headers.get("Content-Type", "image/jpeg")
    ext = ".jpg" if "jpeg" in content_type else ".png" if "png" in content_type else ".jpg"

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    tmp.write(resp.content)
    tmp.close()
    return tmp.name


# ── Poster ────────────────────────────────────────────────────────────────────

def post_to_mastodon(painting: dict):
    mastodon = Mastodon(
        access_token=MASTODON_ACCESS_TOKEN,
        api_base_url=MASTODON_BASE_URL,
    )

    title = painting["title"]
    year  = painting["year"]
    caption = f'"{title}"' + (f", {year}" if year else "") + "\n\nby Pablo Picasso\n\n#Picasso #Art #PabloPicasso #DailyArt"

    # Download and upload image
    img_path = download_image(painting["img_url"])
    try:
        alt_text = f"{title} by Pablo Picasso" + (f", {year}" if year else "")
        media   = mastodon.media_post(img_path, description=alt_text)
        mastodon.status_post(caption, media_ids=[media["id"]], visibility="public")
        print(f"✅ Posted: {title} ({year})")
    finally:
        os.unlink(img_path)


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Fetching paintings…")
    paintings = fetch_paintings()
    print(f"Found {len(paintings)} paintings.")

    painting = random.choice(paintings)
    print(f"Selected: {painting['title']} ({painting['year']})")

    post_to_mastodon(painting)
