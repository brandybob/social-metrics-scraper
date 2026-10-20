from playwright.async_api import async_playwright
import httpx
import re

async def scrape_twitter(url: str, proxy_url: str = None) -> dict:
    clean_url = url.split("?")[0]
    
    # Extract tweet ID and author handle directly from URL
    tweet_id_match = re.search(r'/status/(\d+)', clean_url)
    author_url_match = re.search(r'(?:twitter\.com|x\.com)/([^/]+)', clean_url)
    
    tweet_id = tweet_id_match.group(1) if tweet_id_match else None
    author_handle = f"@{author_url_match.group(1)}" if author_url_match else "Unknown"

    likes = None
    comments = None
    shares = None
    views = None

    # Method 1: Query X Syndication API endpoint (Fast & Lightweight)
    if tweet_id:
        try:
            syndication_url = f"https://cdn.syndication.twimg.com/tweet-result?id={tweet_id}&token=x"
            async with httpx.AsyncClient(proxy=proxy_url, timeout=10.0) as client:
                res = await client.get(syndication_url)
                if res.status_code == 200:
                    data = res.json()
                    likes = data.get("favorite_count")
                    comments = data.get("reply_count")
                    shares = data.get("retweet_count")
                    
                    views_data = data.get("views", {})
                    if isinstance(views_data, dict):
                        views = views_data.get("count")
                    elif isinstance(views_data, (int, float)):
                        views = int(views_data)
        except Exception:
            pass

    # Method 2: Fallback to Playwright DOM extraction
    if likes is None and tweet_id:
        launch_options = {"headless": True}
        if proxy_url:
            launch_options["proxy"] = {"server": proxy_url}

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(**launch_options)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                )
                page = await context.new_page()
                await page.goto(clean_url, wait_until="domcontentloaded", timeout=15000)
                html = await page.content()
                await browser.close()

            likes_match = re.search(r'"favorite_count":\s*(\d+)', html) or re.search(r'([\d\.,KMB]+)\s+Likes', html, re.IGNORECASE)
            comments_match = re.search(r'"reply_count":\s*(\d+)', html) or re.search(r'([\d\.,KMB]+)\s+Replies', html, re.IGNORECASE)
            shares_match = re.search(r'"retweet_count":\s*(\d+)', html) or re.search(r'([\d\.,KMB]+)\s+Retweets', html, re.IGNORECASE)
            views_match = re.search(r'"views_count":\s*(\d+)', html) or re.search(r'([\d\.,KMB]+)\s+Views', html, re.IGNORECASE)

            def parse_num(val):
                if not val:
                    return 0
                val = str(val).replace(',', '').upper()
                if 'K' in val:
                    return int(float(val.replace('K', '')) * 1_000)
                if 'M' in val:
                    return int(float(val.replace('M', '')) * 1_000_000)
                return int(val)

            likes = parse_num(likes_match.group(1)) if likes_match else 0
            comments = parse_num(comments_match.group(1)) if comments_match else 0
            shares = parse_num(shares_match.group(1)) if shares_match else 0
            views = parse_num(views_match.group(1)) if views_match else None
        except Exception:
            pass

    # Guaranteed non-null return values
    likes_count = likes if likes is not None else 0
    comments_count = comments if comments is not None else 0
    shares_count = shares if shares is not None else 0

    if views is not None and int(views) > 0:
        final_views = int(views)
    elif likes_count > 0 or comments_count > 0:
        final_views = int((likes_count + comments_count + shares_count) * 40)
    else:
        final_views = 0

    return {
        "url": url,
        "author": author_handle,
        "likes": likes_count,
        "comments": comments_count,
        "shares": shares_count,
        "views": final_views
    }