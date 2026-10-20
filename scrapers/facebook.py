import httpx
import re

async def scrape_facebook(url: str) -> dict:
    # Use modern browser headers to avoid instant blocking on share links
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            html = response.text

        # Extract author name from meta tags or title
        author = (
            re.search(r'<meta property="og:title" content="([^"]+)"', html) or
            re.search(r'"owner":\s*{\s*"name":\s*"([^"]+)"', html)
        )
        
        # Extract engagement metrics from open graph meta tags and JSON payloads
        likes = re.search(r'"reaction_count":\s*{\s*"count":\s*(\d+)', html) or re.search(r'(\d[\d,]*)\s+likes', html, re.IGNORECASE)
        comments = re.search(r'"comment_count":\s*{\s*"total_count":\s*(\d+)', html) or re.search(r'(\d[\d,]*)\s+comments', html, re.IGNORECASE)
        shares = re.search(r'"share_count":\s*{\s*"count":\s*(\d+)', html) or re.search(r'(\d[\d,]*)\s+shares', html, re.IGNORECASE)
        views = re.search(r'"video_view_count":\s*(\d+)', html)

        author_name = author.group(1).split('|')[0].strip() if author else "Unknown"

        return {
            "url": url,
            "author": author_name,
            "likes": int(likes.group(1).replace(',', '')) if likes else None,
            "comments": int(comments.group(1).replace(',', '')) if comments else None,
            "shares": int(shares.group(1).replace(',', '')) if shares else None,
            "views": int(views.group(1)) if views else None
        }

    except Exception:
        return {
            "url": url,
            "author": "N/A",
            "likes": None,
            "comments": None,
            "shares": None,
            "views": None
        }