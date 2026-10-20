import httpx
import re

async def scrape_instagram(url: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    async with httpx.AsyncClient() as client:
        # Request the Instagram Post/Reel HTML content
        response = await client.get(url, headers=headers, follow_redirects=True)
        html = response.text

    # Extract author, likes, comments, and views from meta tags and scripts
    author = re.search(r'"owner":\s*{\s*"username":\s*"([^"]+)"', html) or re.search(r'instagram\.com/([^/]+)/', url)
    likes = re.search(r'"edge_media_preview_like":\s*{\s*"count":\s*(\d+)', html) or re.search(r'(\d[\d,]*)\s+Likes', html)
    comments = re.search(r'"edge_media_to_parent_comment":\s*{\s*"count":\s*(\d+)', html)
    views = re.search(r'"video_view_count":\s*(\d+)', html)

    # Clean numbers (strip commas if matched from meta tags)
    clean_likes = int(likes.group(1).replace(',', '')) if likes else None

    return {
        "url": url,
        "author": f"@{author.group(1)}" if author else "Unknown",
        "likes": clean_likes,
        "comments": int(comments.group(1)) if comments else None,
        "shares": None,  # Instagram does NOT show public share counts on posts/reels
        "views": int(views.group(1)) if views else None
    }