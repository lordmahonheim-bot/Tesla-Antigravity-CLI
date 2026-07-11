import os
import time
import logging
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# Config logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("reddit_client")

# Load environment variables
load_dotenv()

try:
    import praw  # type: ignore
    from praw.exceptions import PRAWException  # type: ignore
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False
    logger.warning("PRAW package is not installed. RedditClient will operate in Mock Mode.")


class MockReddit:
    """Mock implementation of PRAW Reddit for testing and fallback."""
    class MockUser:
        def me(self) -> Any:
            class MeObj:
                name = "Glittering_Use_5519"
                created_utc = 1609459200
                link_karma = 1234
                comment_karma = 567
            return MeObj()

    class MockRedditor:
        def __init__(self, name: str) -> None:
            self.name = name
            self.created_utc = 1609459200
            self.link_karma = 1000
            self.comment_karma = 200

    class MockSubreddit:
        def __init__(self, name: str) -> None:
            self.display_name = name

        def new(self, limit: int = 10) -> List[Any]:
            posts = []
            for i in range(limit):
                class MockSubmission:
                    id = f"mock_post_{i}"
                    title = f"Mock Title {i} in r/{self.display_name}"
                    selftext = f"Mock body text {i}"
                    author = type("Auth", (object,), {"name": "Glittering_Use_5519"})()
                    created_utc = time.time() - (i * 3600)
                    url = f"https://reddit.com/r/{self.display_name}/comments/{id}"
                    permalink = f"/r/{self.display_name}/comments/{id}"
                posts.append(MockSubmission())
            return posts

        def submit(self, title: str, selftext: str = "", url: Optional[str] = None) -> Any:
            class MockSubmitted:
                id = f"new_post_{int(time.time())}"
                permalink = f"/r/{self.display_name}/comments/{id}"
                url = f"https://reddit.com/r/{self.display_name}/comments/{id}"
            return MockSubmitted()

    def __init__(self, **kwargs: Any) -> None:
        self.user = self.MockUser()
        self.read_only = False

    def subreddit(self, name: str) -> Any:
        return self.MockSubreddit(name)

    def redditor(self, name: str) -> Any:
        return self.MockRedditor(name)

    def submission(self, id: str) -> Any:
        class MockSubmissionObj:
            def reply(self, body: str) -> Any:
                class MockComment:
                    id = f"new_comment_{int(time.time())}"
                    permalink = f"/comments/mock_post/{id}"
                return MockComment()
            
            def edit(self, body: str) -> Any:
                class MockEdited:
                    id = id
                return MockEdited()
        return MockSubmissionObj()

    def comment(self, id: str) -> Any:
        class MockCommentObj:
            def reply(self, body: str) -> Any:
                class MockComment:
                    id = f"new_comment_{int(time.time())}"
                    permalink = f"/comments/mock_post/{id}"
                return MockComment()
            
            def edit(self, body: str) -> Any:
                class MockEdited:
                    id = id
                return MockEdited()
        return MockCommentObj()


class RedditClient:
    """Wrapper around PRAW Reddit Client with Strict Safe Mode controls."""
    
    def __init__(self, mock: bool = False) -> None:
        self.mock_mode = mock or (not PRAW_AVAILABLE)
        self.safe_mode = os.getenv("REDDIT_SAFE_MODE", "true").lower() == "true"
        
        if self.mock_mode:
            logger.info("Initializing RedditClient in MOCK MODE.")
            self.reddit = MockReddit()
        else:
            client_id = os.getenv("REDDIT_CLIENT_ID")
            client_secret = os.getenv("REDDIT_CLIENT_SECRET")
            user_agent = os.getenv("REDDIT_USER_AGENT", "tesla-reddit-commander:v1.0")
            username = os.getenv("REDDIT_USERNAME")
            password = os.getenv("REDDIT_PASSWORD")
            
            if not all([client_id, client_secret, username, password]):
                logger.warning("Missing Reddit API credentials in environment. Falling back to MOCK MODE.")
                self.mock_mode = True
                self.reddit = MockReddit()
            else:
                try:
                    self.reddit = praw.Reddit(
                        client_id=client_id,
                        client_secret=client_secret,
                        user_agent=user_agent,
                        username=username,
                        password=password
                    )
                    logger.info(f"Connected to Reddit API as u/{username}")
                except Exception as e:
                    logger.error(f"Failed to connect to Reddit API: {e}. Falling back to MOCK MODE.")
                    self.mock_mode = True
                    self.reddit = MockReddit()

    def get_user_profile(self, username: str) -> Dict[str, Any]:
        """Fetch user profile details (Read-Only)."""
        try:
            user = self.reddit.redditor(username)
            # Fetch attributes safely
            return {
                "username": getattr(user, "name", username),
                "created_utc": getattr(user, "created_utc", 0.0),
                "link_karma": getattr(user, "link_karma", 0),
                "comment_karma": getattr(user, "comment_karma", 0)
            }
        except Exception as e:
            logger.error(f"Error fetching user profile {username}: {e}")
            raise

    def get_subreddit_posts(self, subreddit_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch recent submissions from a subreddit (Read-Only)."""
        try:
            sub = self.reddit.subreddit(subreddit_name)
            submissions = sub.new(limit=limit)
            result = []
            for post in submissions:
                result.append({
                    "id": post.id,
                    "title": post.title,
                    "body": post.selftext,
                    "author": getattr(post.author, "name", "[deleted]"),
                    "created_utc": post.created_utc,
                    "url": post.url,
                    "permalink": post.permalink
                })
            return result
        except Exception as e:
            logger.error(f"Error fetching posts from r/{subreddit_name}: {e}")
            raise

    def create_post(self, subreddit_name: str, title: str, body: str) -> Dict[str, Any]:
        """Create a new text post in a subreddit (Mutation)."""
        if self.safe_mode:
            logger.warning(f"[SAFE MODE] Prevented post submission to r/{subreddit_name}: '{title}'")
            return {
                "status": "SAFE_MODE_BLOCKED",
                "subreddit": subreddit_name,
                "title": title,
                "body": body,
                "id": "safe_mode_mock_id",
                "permalink": f"/r/{subreddit_name}/comments/safe_mode_mock_id"
            }
        
        try:
            sub = self.reddit.subreddit(subreddit_name)
            post = sub.submit(title=title, selftext=body)
            logger.info(f"Successfully posted to r/{subreddit_name}: {post.permalink}")
            return {
                "status": "SUCCESS",
                "subreddit": subreddit_name,
                "title": title,
                "body": body,
                "id": post.id,
                "permalink": post.permalink
            }
        except Exception as e:
            logger.error(f"Failed to submit post to r/{subreddit_name}: {e}")
            raise

    def create_comment(self, parent_id: str, body: str) -> Dict[str, Any]:
        """Create a comment reply to a post or comment (Mutation)."""
        if self.safe_mode:
            logger.warning(f"[SAFE MODE] Prevented comment reply to parent {parent_id}: '{body[:30]}...'")
            return {
                "status": "SAFE_MODE_BLOCKED",
                "parent_id": parent_id,
                "body": body,
                "id": "safe_mode_mock_id",
                "permalink": f"/comments/mock_post/safe_mode_mock_id"
            }

        try:
            if parent_id.startswith("t3_"):
                parent = self.reddit.submission(id=parent_id[3:])
            elif parent_id.startswith("t1_"):
                parent = self.reddit.comment(id=parent_id[3:])
            else:
                parent = self.reddit.submission(id=parent_id)
            
            comment = parent.reply(body)
            logger.info(f"Successfully added comment to {parent_id}: {comment.permalink}")
            return {
                "status": "SUCCESS",
                "parent_id": parent_id,
                "body": body,
                "id": comment.id,
                "permalink": comment.permalink
            }
        except Exception as e:
            logger.error(f"Failed to reply to {parent_id}: {e}")
            raise

    def edit_content(self, item_id: str, body: str) -> Dict[str, Any]:
        """Edit an existing post or comment (Mutation)."""
        if self.safe_mode:
            logger.warning(f"[SAFE MODE] Prevented editing item {item_id}")
            return {
                "status": "SAFE_MODE_BLOCKED",
                "item_id": item_id,
                "body": body
            }

        try:
            if item_id.startswith("t3_"):
                item = self.reddit.submission(id=item_id[3:])
            elif item_id.startswith("t1_"):
                item = self.reddit.comment(id=item_id[3:])
            else:
                item = self.reddit.submission(id=item_id)
            
            item.edit(body)
            logger.info(f"Successfully edited item {item_id}")
            return {
                "status": "SUCCESS",
                "item_id": item_id,
                "body": body
            }
        except Exception as e:
            logger.error(f"Failed to edit item {item_id}: {e}")
            raise

    def vote(self, item_id: str, direction: int) -> None:
        """Vote on an item (Strictly forbidden mutation)."""
        raise PermissionError("Automated karma voting is strictly forbidden under the Vigilum Codex.")

    def send_private_message(self, recipient: str, subject: str, body: str) -> None:
        """Send private messages (Strictly forbidden mutation)."""
        raise PermissionError("Automated private messaging is strictly forbidden under the Vigilum Codex.")
