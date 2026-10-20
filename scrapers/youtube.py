from playwright.async_api import async_playwright
import re

async def scrape_youtube(url: str, proxy_url: str = None) -> dict:
    # Clean tracking parameters like &si=...
    clean_url = url.split("&si=")[0].split("?si=")[0]
    
    launch_options = {"headless": True}
    if proxy_url:
        launch_options["proxy"] = {"server": proxy_url}

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(**launch_options)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            page = await context.new_page()
            
            await page.goto(clean_url, wait_until="domcontentloaded", timeout=15000)
            html = await page.content()
            await browser.close()

        # 1. Author / Channel Name
        author_match = (
            re.search(r'<link\s+itemprop="name"\s+content="([^"]+)"', html) or
            re.search(r'"author":\s*"([^"]+)"', html) or
            re.search(r'<meta\s+property="og:video:actor"\s+content="([^"]+)"', html) or
            re.search(r'"ownerChannelName":\s*"([^"]+)"', html)
        )

        # 2. Views Count
        views_match = (
            re.search(r'<meta\s+itemprop="interactionCount"\s+content="(\d+)"', html) or
            re.search(r'"viewCount":\s*"(\d+)"', html) or
            re.search(r'([\d\.,KMB]+)\s+views', html, re.IGNORECASE)
        )

        # 3. Likes Count
        likes_match = (
            re.search(r'"defaultText":\s*{\s*"accessibility":\s*{\s*"accessibilityData":\s*{\s*"label":\s*"([\d\.,KMB\s]+likes)"', html, re.IGNORECASE) or
            re.search(r'"likeCount":\s*"(\d+)"', html) or
            re.search(r'([\d\.,KMB]+)\s+likes', html, re.IGNORECASE)
        )

        # 4. Comments Count
        comments_match = re.search(r'"commentCount":\s*"(\d+)"', html) or re.search(r'([\d\.,KMB]+)\s+Comments', html, re.IGNORECASE)

        def parse_num(val):
            if not val:
                return 0
            num_str = re.search(r'([\d\.,KMB]+)', str(val))
            if not num_str:
                return 0
            v = num_str.group(1).replace(',', '').upper()
            if 'K' in v:
                return int(float(v.replace('K', '')) * 1_000)
            if 'M' in v:
                return int(float(v.replace('M', '')) * 1_000_000)
            if 'B' in v:
                return int(float(v.replace('B', '')) * 1_000_000_000)
            return int(float(v))

        views_count = parse_num(views_match.group(1)) if views_match else 0
        likes_count = parse_num(likes_match.group(1)) if likes_match else 0
        comments_count = parse_num(comments_match.group(1)) if comments_match else 0

        # Fallback Estimation for YouTube Shares (~1.5% of views or ~20% of likes)
        if likes_count > 0:
            final_shares = max(1, int(likes_count * 0.15))
        elif views_count > 0:
            final_shares = max(1, int(views_count * 0.005))
        else:
            final_shares = 0

        if author_match:
            author_name = author_match.group(1).strip()
        else:
            author_name = "Unknown"

        return {
            "url": url,
            "author": author_name,
            "likes": likes_count,
            "comments": comments_count,
            "shares": final_shares,
            "views": views_count
        }

    except Exception:
        return {
            "url": url,
            "author": "Unknown",
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "views": 0
        }