from apify import Actor

async def scrape_facebook(url: str, proxy_url: str = None) -> dict:
    try:
        run = await Actor.call(
            "apify/facebook-posts-scraper",
            run_input={
                "startUrls": [{"url": url}],
                "resultsLimit": 1
            }
        )
        
        dataset = await Actor.apify_client.dataset(run.default_dataset_id).list_items()
        items = dataset.items
        
        if not items:
            raise Exception("No data returned from the dedicated Facebook Actor.")
            
        post_data = items[0]
        
        # 1. Extract raw metrics
        likes = post_data.get("likes", 0)
        comments = post_data.get("comments", 0)
        shares = post_data.get("shares", 0)
        views = post_data.get("views", 0) 
        
        # 2. Ensure clean integers
        likes_count = int(likes) if likes else 0
        comments_count = int(comments) if comments else 0
        shares_count = int(shares) if shares else 0
        extracted_views = int(views) if views else 0
        
        # 3. Fallback Estimation Logic for Views (approx 3% engagement rate)
        if extracted_views > 0:
            final_views = extracted_views
        elif likes_count > 0 or comments_count > 0:
            final_views = (likes_count + comments_count + shares_count) * 30
        else:
            final_views = 0
            
        author_name = post_data.get("user", {}).get("name") or post_data.get("pageName") or "Unknown"
        
        return {
            "url": url,
            "author": author_name,
            "likes": likes_count,
            "comments": comments_count,
            "shares": shares_count,
            "views": final_views
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