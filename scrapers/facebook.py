import httpx
import re

async def scrape_facebook(url: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, follow_redirects=True)
        html = response.text

    # Extract author and engagement counts from public page metadata
    author = re.search(r'"owner":\s*{\s*"name":\s*"([^"]+)"', html) or re.search(r'facebook\.com/([^/]+)', url)
    likes = re.search(r'"reaction_count":\s*{\s*"count":\s*(\d+)', html) or re.search(r'(\d[\d,]*)\s+likes', html, re.IGNORECASE)
    comments = re.search(r'"comment_count":\s*{\s*"total_count":\s*(\d+)', html) or re.search(r'(\d[\d,]*)\s+comments', html, re.IGNORECASE)
    shares = re.search(r'"share_count":\s*{\s*"count":\s*(\d+)', html) or re.search(r'(\d[\d,]*)\s+shares', html, re.IGNORECASE)
    views = re.search(r'"video_view_count":\s*(\d+)', html)

    return {
        "url": url,
        "author": author.group(1) if author else "Unknown",
        "likes": int(likes.group(1).replace(',', '')) if likes else None,
        "comments": int(comments.group(1).replace(',', '')) if comments else None,
        "shares": int(shares.group(1).replace(',', '')) if shares else None,
        "views": int(views.group(1)) if views else None
    }