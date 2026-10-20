import httpx
import re

async def scrape_linkedin(url: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    async with httpx.AsyncClient() as client:
        # Request the public post page
        response = await client.get(url, headers=headers, follow_redirects=True)
        html = response.text

    # Extract metrics from public meta tags / JSON embedded data
    author = re.search(r'"author":\s*{\s*"name":\s*"([^"]+)"', html) or re.search(r'linkedin\.com/in/([^/]+)', url)
    likes = re.search(r'"numLikes":\s*(\d+)', html) or re.search(r'(\d[\d,]*)\s+reactions', html, re.IGNORECASE)
    comments = re.search(r'"numComments":\s*(\d+)', html) or re.search(r'(\d[\d,]*)\s+comments', html, re.IGNORECASE)

    clean_likes = int(likes.group(1).replace(',', '')) if likes else None
    clean_comments = int(comments.group(1).replace(',', '')) if comments else None

    return {
        "url": url,
        "author": author.group(1) if author else "Unknown",
        "likes": clean_likes,
        "comments": clean_comments,
        "shares": None,  # LinkedIn public posts do not reliably expose repost/share counts without login
        "views": None   # Post views on LinkedIn are private to the author only
    }