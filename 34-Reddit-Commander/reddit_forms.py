import os
import sys
import time
import logging
from typing import Optional
from playwright.sync_api import sync_playwright, Page, BrowserContext

logger = logging.getLogger("reddit_forms")

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_DATA_DIR = os.path.join(WORKSPACE_DIR, ".runtime", "playwright_reddit_user")


def detect_challenge(page: Page) -> Optional[str]:
    """Inspect the page for active CAPTCHAs, 2FA prompts, or age gates."""
    captcha_selectors = [
        "iframe[src*='recaptcha']",
        "iframe[src*='hcaptcha']",
        "iframe[src*='arkose']",
        "div[class*='captcha']",
        "#captcha",
        ".g-recaptcha"
    ]
    for sel in captcha_selectors:
        try:
            if page.locator(sel).is_visible():
                return f"CAPTCHA detected (selector: {sel})"
        except Exception:
            pass

    tfa_selectors = [
        "input[name*='2fa']",
        "input[id*='2fa']",
        "input[name*='totp']",
        "input[name*='code']"
    ]
    for sel in tfa_selectors:
        try:
            if page.locator(sel).is_visible() and "login" in page.url:
                return f"2FA/Verification Code input field detected (selector: {sel})"
        except Exception:
            pass

    age_gate_selectors = [
        "button:has-text('Yes, I am over 18')",
        "a:has-text('Over 18')",
        "button:has-text('Continue')"
    ]
    for sel in age_gate_selectors:
        try:
            if page.locator(sel).is_visible() and "over18" in page.content().lower():
                return f"Age gate / NSFW prompt detected (selector: {sel})"
        except Exception:
            pass

    return None


def run_human_verification_gate(page: Page, reason: str) -> None:
    """Pause the script, alert the operator, and wait for human completion."""
    print("\n" + "=" * 80)
    print(f"!!! [HUMAN VERIFICATION GATE TRIGGERED] !!!")
    print(f"Reason: {reason}")
    print(f"Please resolve this security challenge or log in manually in the opened browser window.")
    print("Do NOT close the browser window. Once you have resolved the gate, return here.")
    print("=" * 80)
    
    try:
        input("\n>>> Action required: Resolve the challenge in the browser and press [ENTER] to resume... ")
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(1)
        
    print("[*] Resuming automation. Re-checking page state...")


class RedditFormsEngine:
    """Engine to assist with complex forms and authentication using Playwright (headed mode)."""
    
    def __init__(self) -> None:
        self.playwright = None
        self.context: Optional[BrowserContext] = None

    def start_session(self) -> Page:
        """Start a headed browser session with a persistent user data directory."""
        os.makedirs(USER_DATA_DIR, exist_ok=True)
        self.playwright = sync_playwright().start()
        
        logger.info(f"Starting Playwright headed browser session. Cache: {USER_DATA_DIR}")
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = self.context.pages[0]
        return page

    def close(self) -> None:
        """Clean up resources."""
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Playwright session closed.")

    def ensure_logged_in(self, page: Page) -> None:
        """Navigate to Reddit and verify if user is logged in, triggering gate if needed."""
        page.goto("https://www.reddit.com/", wait_until="domcontentloaded")
        time.sleep(2)
        
        is_logged_in = False
        try:
            if page.locator("#user-drawer-button").is_visible() or page.locator("a[href*='/submit']").is_visible():
                is_logged_in = True
        except Exception:
            pass
            
        if not is_logged_in:
            logger.info("Not logged in. Navigating to login page.")
            page.goto("https://www.reddit.com/login/", wait_until="domcontentloaded")
            time.sleep(2)
            
            username = os.getenv("REDDIT_USERNAME")
            password = os.getenv("REDDIT_PASSWORD")
            
            if username and password:
                try:
                    page.fill("#login-username", username)
                    page.fill("#login-password", password)
                    page.click("button[type='submit']")
                    time.sleep(3)
                except Exception as e:
                    logger.warning(f"Could not fill login form automatically: {e}")
            
            challenge_reason = detect_challenge(page)
            if challenge_reason:
                run_human_verification_gate(page, challenge_reason)
            
            while True:
                challenge_reason = detect_challenge(page)
                if challenge_reason:
                    run_human_verification_gate(page, challenge_reason)
                    continue
                
                try:
                    if page.locator("a[href*='/submit']").is_visible() or not page.locator("a[href*='/login']").is_visible():
                        logger.info("Login confirmed.")
                        break
                except Exception:
                    pass
                
                print("\n[*] Still not logged in. If you completed login and 2FA, press [ENTER] to check again.")
                run_human_verification_gate(page, "Manual login confirmation")

    def autofill_post(self, subreddit: str, title: str, body: str) -> None:
        """Autofill a submit form on Reddit and let the user review it."""
        page = self.start_session()
        try:
            self.ensure_logged_in(page)
            
            logger.info(f"Navigating to submit post page for r/{subreddit}")
            page.goto(f"https://www.reddit.com/r/{subreddit}/submit", wait_until="domcontentloaded")
            time.sleep(3)
            
            challenge_reason = detect_challenge(page)
            if challenge_reason:
                run_human_verification_gate(page, challenge_reason)

            try:
                title_selector = "textarea[placeholder='Title']"
                body_selector = "div[role='textbox']"
                
                page.wait_for_selector(title_selector, timeout=10000)
                page.fill(title_selector, title)
                
                if page.locator(body_selector).is_visible():
                    page.fill(body_selector, body)
                else:
                    page.fill("textarea[placeholder='Text (optional)']", body)
                    
                logger.info("Form fields filled. Awaiting manual user review/submission.")
                
            except Exception as e:
                logger.error(f"Error autofilling form fields: {e}")
                print("\n[!] AutoFill failed to find some inputs. Please fill them manually.")
            
            run_human_verification_gate(page, "Operator review and manual submission validation")
            
        finally:
            self.close()

    def autofill_comment(self, url: str, body: str) -> None:
        """Autofill a comment box on a specific Reddit thread/post."""
        page = self.start_session()
        try:
            self.ensure_logged_in(page)
            
            logger.info(f"Navigating to post: {url}")
            page.goto(url, wait_until="domcontentloaded")
            time.sleep(3)
            
            challenge_reason = detect_challenge(page)
            if challenge_reason:
                run_human_verification_gate(page, challenge_reason)
                
            try:
                comment_selector = "div[role='textbox']"
                page.wait_for_selector(comment_selector, timeout=10000)
                page.fill(comment_selector, body)
                logger.info("Comment text filled. Awaiting manual user review/submission.")
            except Exception as e:
                logger.error(f"Error autofilling comment box: {e}")
                print("\n[!] AutoFill failed to find the comment box. Please fill it manually.")
                
            run_human_verification_gate(page, "Operator review and manual comment submission")
            
        finally:
            self.close()
