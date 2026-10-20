from playwright.async_api import async_playwright
import re

async def scrape_facebook(url: str, proxy_url: str = None) -> dict:
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
            
            # Wait for the page to navigate through the /share/ redirect
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            html = await page.content()
            await browser.close()

        # Extract Meta Tags
        meta_title = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', html)
        meta_desc = re.search(r'<meta\s+property="og:description"\s+content="([^"]+)"', html)
        
        title_text = meta_title.group(1) if meta_title else ""
        desc_text = meta_desc.group(1) if meta_desc else ""

        # Extract Metrics (handles both embedded JSON and standard text formats)
        likes_match = (
            re.search(r'"reaction_count":\s*{\s*"count":\s*(\d+)', html) or 
            re.search(r'([\d\.,KMB]+)\s+Likes', desc_text, re.IGNORECASE) or 
            re.search(r'([\d\.,KMB]+)\s+likes', html, re.IGNORECASE)
        )
        comments_match = (
            re.search(r'"comment_count":\s*{\s*"total_count":\s*(\d+)', html) or 
            re.search(r'([\d\.,KMB]+)\s+Comments', desc_text, re.IGNORECASE) or 
            re.search(r'([\d\.,KMB]+)\s+comments', html, re.IGNORECASE)
        )
        shares_match = (
            re.search(r'"share_count":\s*{\s*"count":\s*(\d+)', html) or 
            re.search(r'([\d\.,KMB]+)\s+Shares', desc_text, re.IGNORECASE) or 
            re.search(r'([\d\.,KMB]+)\s+shares', html, re.IGNORECASE)
        )
        views_match = (
            re.search(r'"video_view_count":\s*(\d+)', html) or 
            re.search(r'([\d\.,KMB]+)\s+Views', desc_text, re.IGNORECASE) or 
            re.search(r'([\d\.,KMB]+)\s+views', html, re.IGNORECASE)
        )

        author_match = (
            re.search(r'"owner":\s*{\s*"name":\s*"([^"]+)"', html) or
            re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', html)
        )

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

        likes_count = parse_num(likes_match.group(1)) if likes_match else 0
        comments_count = parse_num(comments_match.group(1)) if comments_match else 0
        shares_count = parse_num(shares_match.group(1)) if shares_match else 0
        views_count = parse_num(views_match.group(1)) if views_match else 0

        # Author parsing (removes appended sitenames like " | Facebook")
        if author_match:
            author_name = author_match.group(1).split('|')[0].strip()
        else:
            author_name = "Unknown"

        return {
            "url": url,
            "author": author_name,
            "likes": likes_count,
            "comments": comments_count,
            "shares": shares_count,
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