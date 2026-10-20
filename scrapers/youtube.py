import httpx
import re

async def scrape_youtube(url: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, follow_redirects=True)
        html = response.text

    # Extract metrics using regex pattern matching on YouTube's raw metadata
    views = re.search(r'"viewCount":"(\d+)"', html)
    likes = re.search(r'"likeCount":"(\d+)"', html)
    author = re.search(r'"author":"([^"]+)"', html)

    return {
        "url": url,
        "author": author.group(1) if author else "Unknown",
        "likes": int(likes.group(1)) if likes else None,
        "comments": None,  # Requires JS execution or API
        "shares": None,    # YouTube does not expose share counts publicly
        "views": int(views.group(1)) if views else None
    }