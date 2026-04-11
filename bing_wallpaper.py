#!/usr/bin/env python3
"""Fetch daily Bing wallpaper and update README."""

import json
import os
import re
import ssl
import urllib.request

try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = None

BING_API = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&nc=1620441890644&pid=hp"
BING_BASE = "https://www.bing.com"
README_PATH = "README.md"
WALLPAPER_PATH = "bing-wallpaper.md"


def fetch_wallpaper():
    """Fetch today's wallpaper info from Bing API."""
    req = urllib.request.Request(BING_API, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    with urllib.request.urlopen(req, context=SSL_CONTEXT) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    image = data["images"][0]
    url = BING_BASE + image["url"].split("&")[0]
    date_str = image["enddate"]
    date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    desc = image["copyright"]

    return {"date": date, "desc": desc, "url": url}


def read_wallpapers():
    """Read existing wallpaper entries from bing-wallpaper.md."""
    if not os.path.exists(WALLPAPER_PATH):
        return []

    wallpapers = []
    with open(WALLPAPER_PATH, "r", encoding="utf-8") as f:
        for line in f:
            match = re.match(r"(\d{4}-\d{2}-\d{2})\s*\|\s*\[(.+?)]\((.+?)\)", line.strip())
            if match:
                wallpapers.append({
                    "date": match.group(1),
                    "desc": match.group(2),
                    "url": match.group(3),
                })
    return wallpapers


def write_wallpaper_md(wallpapers):
    """Write bing-wallpaper.md as persistent data store."""
    with open(WALLPAPER_PATH, "w", encoding="utf-8") as f:
        f.write("## Bing Wallpaper\n\n")
        for wp in wallpapers:
            f.write(f"{wp['date']} | [{wp['desc']}]({wp['url']})\n")


def write_readme(wallpapers):
    """Write README.md with hero image and 2-column thumbnail grid."""
    if not wallpapers:
        return

    today = wallpapers[0]
    lines = [
        "## Bing Wallpaper",
        "",
        f"![{today['desc']}]({today['url']}&w=1000)",
        "",
        f"Today: [{today['desc']}]({today['url']})",
        "",
        "|      |      |",
        "| :----: | :----: |",
    ]

    row = []
    for wp in wallpapers:
        cell = (
            f"![]({wp['url']}&pid=hp&w=384&h=216&rs=1&c=4)"
            f"<br>{wp['date']} [download 4k]({wp['url']})"
        )
        row.append(cell)
        if len(row) == 2:
            lines.append(f"|{row[0]}|{row[1]}|")
            row = []

    if row:
        lines.append(f"|{row[0]}| |")

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    print("Fetching Bing wallpaper...")
    new_wp = fetch_wallpaper()
    print(f"Got: {new_wp['date']} - {new_wp['desc']}")

    wallpapers = read_wallpapers()

    # Deduplicate by date
    if not any(wp["date"] == new_wp["date"] for wp in wallpapers):
        wallpapers.insert(0, new_wp)
        print("Added new wallpaper entry.")
    else:
        print("Wallpaper for this date already exists, skipping.")

    write_wallpaper_md(wallpapers)
    write_readme(wallpapers)
    print("Updated README.md and bing-wallpaper.md")


if __name__ == "__main__":
    main()
