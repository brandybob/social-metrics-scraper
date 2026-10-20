import asyncio
from urllib.parse import urlparse
from apify import Actor
from scrapers.youtube import scrape_youtube

def detect_platform(url: str) -> str:
    """Extracts domain name to figure out the platform."""
    domain = urlparse(url).netloc.lower()
    if "youtube.com" in domain or "youtu.be" in domain:
        return "youtube"
    elif "tiktok.com" in domain:
        return "tiktok"
    elif "instagram.com" in domain:
        return "instagram"
    elif "twitter.com" in domain or "x.com" in domain:
        return "twitter"
    elif "facebook.com" in domain:
        return "facebook"
    elif "linkedin.com" in domain:
        return "linkedin"
    return "unknown"

async def main():
    # Initializes the Apify environment lifecycle
    async with Actor:
        # 1. Fetch input provided by the user
        actor_input = await Actor.get_input() or {}
        urls = actor_input.get("urls", [])

        if not urls:
            Actor.log.info("No URLs were provided. Stopping Actor.")
            return

        # 2. Iterate through each URL and route it
        for url in urls:
            platform = detect_platform(url)
            Actor.log.info(f"Processing URL: {url} | Identified Platform: {platform}")

            data = None
            if platform == "youtube":
                data = await scrape_youtube(url)
            else:
                # Fallback structure for unsupported or pending platform modules
                data = {
                    "url": url,
                    "author": "N/A",
                    "likes": None,
                    "comments": None,
                    "shares": None,
                    "views": None
                }

            # 3. Push dataset row to Apify storage
            if data:
                await Actor.push_data(data)

if __name__ == "__main__":
    asyncio.run(main())