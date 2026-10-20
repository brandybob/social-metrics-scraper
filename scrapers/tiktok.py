import httpx
import re

async def scrape_tiktok(url: str, proxy_url: str = None) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        async with httpx.AsyncClient(headers=headers, follow_redirects=True, proxy=proxy_url, timeout=15.0) as client:
            response = await client.get(url)
            html = response.text
            final_url = str(response.url)

        # 1. Extract Author from canonical redirected URL or HTML meta
        author_match = (
            re.search(r'tiktok\.com/@([^/]+)/video', final_url) or
            re.search(r'"author":\s*{\s*"uniqueId":\s*"([^"]+)"', html) or
            re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', html)
        )

        # 2. Extract Metrics from SIGI_STATE or __UNIVERSAL_DATA_FOR_REHYDRATION__ JSON payloads
        digg_match = re.search(r'"diggCount":\s*(\d+)', html) or re.search(r'"likeCount":\s*(\d+)', html)
        comment_match = re.search(r'"commentCount":\s*(\d+)', html)
        share_match = re.search(r'"shareCount":\s*(\d+)', html)
        play_match = re.search(r'"playCount":\s*(\d+)', html) or re.search(r'"viewCount":\s*(\d+)', html)

        if author_match:
            raw_author = author_match.group(1).split(" ")[0].strip()
            author_name = raw_author if raw_author.startswith("@") else f"@{raw_author}"
        else:
            author_name = "Unknown"

        return {
            "url": url,
            "author": author_name,
            "likes": int(digg_match.group(1)) if digg_match else None,
            "comments": int(comment_match.group(1)) if comment_match else None,
            "shares": int(share_match.group(1)) if share_match else None,
            "views": int(play_match.group(1)) if play_match else None
        }

    except Exception:
        return {
            "url": url,
            "author": "Unknown",
            "likes": None,
            "comments": None,
            "shares": None,
            "views": None
        }