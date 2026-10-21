from apify import Actor

async def scrape_facebook(url: str, proxy_url: str = None) -> dict:
    try:
        # 1. Call a maintained Apify Facebook scraper to do the heavy lifting
        # (This Actor automatically handles login walls and Facebook's complex HTML)
        run = await Actor.call(
            "apify/facebook-posts-scraper",
            run_input={
                "startUrls": [{"url": url}],
                "resultsLimit": 1
            }
        )
        
        # 2. Fetch the extracted data from that Actor's default dataset
        dataset = await Actor.apify_client.dataset(run["defaultDatasetId"]).list_items()
        items = dataset.items
        
        if not items:
            raise Exception("No data returned from the dedicated Facebook Actor.")
            
        post_data = items[0]
        
        # 3. Standardize the data to match your dataset schema
        likes = post_data.get("likes", 0)
        comments = post_data.get("comments", 0)
        shares = post_data.get("shares", 0)
        
        # Facebook doesn't typically expose views on regular posts via this API, but we check just in case
        views = post_data.get("views", 0) 
        
        # Extract author name (varies slightly depending on page vs user)
        author_name = post_data.get("user", {}).get("name") or post_data.get("pageName") or "Unknown"
        
        return {
            "url": url,
            "author": author_name,
            "likes": int(likes) if likes else 0,
            "comments": int(comments) if comments else 0,
            "shares": int(shares) if shares else 0,
            "views": int(views) if views else 0
        }

    except Exception as e:
        Actor.log.warning(f"Facebook delegation failed for {url}: {e}")
        return {
            "url": url,
            "author": "Unknown",
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "views": 0
        }