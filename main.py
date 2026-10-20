import asyncio
from urllib.parse import urlparse
from apify import Actor

from scrapers.youtube import scrape_youtube
from scrapers.tiktok import scrape_tiktok
from scrapers.instagram import scrape_instagram
from scrapers.linkedin import scrape_linkedin
from scrapers.facebook import scrape_facebook
from scrapers.twitter import scrape_twitter

def detect_platform(url: str) -> str:
    domain = urlparse(url).netloc.lower()
    if "youtube.com" in domain or "youtu.be" in domain:
        return "youtube"
    elif "tiktok.com" in domain:
        return "tiktok"
    elif "instagram.com" in domain:
        return "instagram"
    elif "linkedin.com" in domain:
        return "linkedin"
    elif "facebook.com" in domain or "fb.watch" in domain:
        return "facebook"
    elif "twitter.com" in domain or "x.com" in domain:
        return "twitter"
    return "unknown"

async def main():
    async with Actor:
        actor_input = await Actor.get_input() or {}
        urls = actor_input.get("urls", [])

        if not urls:
            Actor.log.info("No URLs provided in input. Exiting.")
            return

        # Initialize Apify Proxy Configuration
        proxy_configuration = await Actor.create_proxy_configuration()
        proxy_url = await proxy_configuration.new_url() if proxy_configuration else None

        for url in urls:
            platform = detect_platform(url)
            Actor.log.info(f"Processing URL: {url} | Platform: [{platform.upper()}]")

            data = None
            if platform == "youtube":
                data = await scrape_youtube(url)
            elif platform == "tiktok":
                data = await scrape_tiktok(url)
            elif platform == "instagram":
                data = await scrape_instagram(url)
            elif platform == "linkedin":
                data = await scrape_linkedin(url)
            elif platform == "facebook":
                data = await scrape_facebook(url)
            elif platform == "twitter":
                data = await scrape_twitter(url)
            else:
                data = {
                    "url": url,
                    "author": "Unsupported Platform",
                    "likes": None,
                    "comments": None,
                    "shares": None,
                    "views": None
                }

            await Actor.push_data(data)

if __name__ == "__main__":
    asyncio.run(main())