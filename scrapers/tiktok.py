import httpx
import re

async def scrape_tiktok(url: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient() as client:
        # Send HTTP request to the TikTok URL
        response = await client.get(url, headers=headers, follow_redirects=True)
        html = response.text

    # Extract metrics using regular expressions (regex) matching TikTok's metadata JSON
    likes = re.search(r'"diggCount":(\d+)', html)
    comments = re.search(r'"commentCount":(\d+)', html)
    shares = re.search(r'"shareCount":(\d+)', html)
    views = re.search(r'"playCount":(\d+)', html)
    author = re.search(r'"uniqueId":"([^"]+)"', html)

    return {
        "url": url,
        "author": f"@{author.group(1)}" if author else "Unknown",
        "likes": int(likes.group(1)) if likes else None,
        "comments": int(comments.group(1)) if comments else None,
        "shares": int(shares.group(1)) if shares else None,
        "views": int(views.group(1)) if views else None
    }