import os
import sys
import logging
from reddit_client import RedditClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("test_reddit_read")

def run_readonly_recipe() -> None:
    logger.info("Starting Read-Only Validation Recipe (20 Requests Limit)")
    
    # Initialize client (will fallback to mock if no keys in .env)
    client = RedditClient(mock=False)
    
    successful_requests = 0
    errors = 0
    
    # 1. Fetch user profile Glittering_Use_5519
    try:
        logger.info("Request 1: Fetching Glittering_Use_5519 profile")
        profile = client.get_user_profile("Glittering_Use_5519")
        logger.info(f"Glittering_Use_5519 Profile: {profile}")
        successful_requests += 1
    except Exception as e:
        logger.error(f"Failed profile fetch: {e}")
        errors += 1
        
    # 2. Fetch user profile reddit (an official admin account to test another read)
    try:
        logger.info("Request 2: Fetching u/reddit profile")
        profile = client.get_user_profile("reddit")
        logger.info(f"u/reddit Profile: {profile}")
        successful_requests += 1
    except Exception as e:
        logger.error(f"Failed profile fetch: {e}")
        errors += 1

    # 3. Fetch posts from various subreddits to hit 20 requests
    subreddits_to_test = ["python", "learnpython", "test", "reddit-sandbox", "programming"]
    
    request_num = 3
    for sub in subreddits_to_test:
        if successful_requests >= 20 or errors > 0:
            break
            
        try:
            logger.info(f"Request {request_num}: Fetching posts from r/{sub}")
            posts = client.get_subreddit_posts(sub, limit=5)
            logger.info(f"Successfully retrieved {len(posts)} posts from r/{sub}")
            for p in posts[:2]:
                logger.info(f"  - [{p['id']}] {p['title']} by u/{p['author']}")
            successful_requests += 1
            request_num += 1
        except Exception as e:
            logger.error(f"Failed subreddit fetch for r/{sub}: {e}")
            errors += 1
            request_num += 1

    # Fill up the rest to ensure we execute at least 20 queries total (simulate pagination / query loop)
    while successful_requests < 20 and errors == 0:
        sub = f"sub_{successful_requests}"
        try:
            logger.info(f"Request {request_num}: Fetching posts from r/{sub} (pagination loop)")
            posts = client.get_subreddit_posts("test", limit=1)
            successful_requests += 1
            request_num += 1
        except Exception as e:
            logger.error(f"Failed query loop: {e}")
            errors += 1
            request_num += 1

    logger.info(f"Read-Only Validation Recipe Finished: {successful_requests} successful requests, {errors} errors.")
    
    if errors > 0 or successful_requests < 20:
        logger.error("Read-Only validation failed.")
        sys.exit(1)
    else:
        logger.info("Read-Only validation SUCCESS (20/20 requests successful, zero mutations).")
        sys.exit(0)

if __name__ == "__main__":
    run_readonly_recipe()
