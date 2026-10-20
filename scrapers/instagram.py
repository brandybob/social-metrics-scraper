from playwright.async_api import async_playwright
import re

async def scrape_instagram(url: str, proxy_url: str = None) -> dict:
    # Clean tracking parameters from URL
    clean_url = url.split("?")[0]
    
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
            
            # Go to link and wait for DOM load
            await page.goto(clean_url, wait_until="domcontentloaded", timeout=15000)
            html = await page.content()
            await browser.close()

        # Extract Meta Title / Description content
        # Example: "15K likes, 230 comments - username on Month Day, Year..."
        meta_desc = re.search(r'<meta\s+property="og:description"\s+content="([^"]+)"', html)
        meta_title = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', html)

        desc_text = meta_desc.group(1) if meta_desc else ""
        title_text = meta_title.group(1) if meta_title else ""

        # Parse metrics using regex patterns
        likes_match = re.search(r'([\d\.,KMB]+)\s+likes', desc_text, re.IGNORECASE)
        comments_match = re.search(r'([\d\.,KMB]+)\s+comments', desc_text, re.IGNORECASE)
        
        # Author extraction from title "Author (@username) on Instagram"
        author_match = re.search(r'\(@([^)]+)\)', title_text) or re.search(r'-\s*([^@]+)\s+on\s+Instagram', title_text)

        def parse_number(val: str):
            if not val:
                return None
            val = val.replace(',', '').upper()
            if 'K' in val:
                return int(float(val.replace('K', '')) * 1_000)
            if 'M' in val:
                return int(float(val.replace('M', '')) * 1_000_000)
            if 'B' in val:
                return int(float(val.replace('B', '')) * 1_000_000_000)
            return int(val)

        author_name = f"@{author_match.group(1)}" if author_match else "Unknown"

        return {
            "url": url,
            "author": author_name,
            "likes": parse_number(likes_match.group(1)) if likes_match else None,
            "comments": parse_number(comments_match.group(1)) if comments_match else None,
            "shares": None,  # Instagram doesn't expose public share counts
            "views": None
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