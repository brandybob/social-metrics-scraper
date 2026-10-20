import httpx
import re

async def scrape_twitter(url: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Extract author username directly from Tweet URL layout
    url_author = re.search(r'(?:twitter\.com|x\.com)/([^/]+)/status', url)
    author_name = f"@{url_author.group(1)}" if url_author else "Unknown"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, follow_redirects=True)
        html = response.text

    # Match public metrics
    likes = re.search(r'"favorite_count":\s*(\d+)', html)
    comments = re.search(r'"reply_count":\s*(\d+)', html)
    shares = re.search(r'"retweet_count":\s*(\d+)', html)  # Retweets = Shares
    views = re.search(r'"views":\s*{\s*"state":\s*"[^{]*",\s*"count":\s*"(\d+)"', html)

    return {
        "url": url,
        "author": author_name,
        "likes": int(likes.group(1)) if likes else None,
        "comments": int(comments.group(1)) if comments else None,
        "shares": int(shares.group(1)) if shares else None,  # Maps Retweets to Shares
        "views": int(views.group(1)) if views else None
    }