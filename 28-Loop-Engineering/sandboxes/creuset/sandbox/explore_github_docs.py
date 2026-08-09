import asyncio
import os
from playwright.async_api import async_playwright

async def explore_github():
    print("[*] Starting Playwright...")
    async with async_playwright() as p:
        # Launch browser local (Firefox preferred for robustness against fingerprinting, or Chromium)
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 1800})
        
        target_url = "https://docs.github.com/en/communities"
        print(f"[*] Navigating to {target_url}...")
        
        try:
            await page.goto(target_url, wait_until="networkidle", timeout=30000)
            print("[+] Navigation successful.")
            
            # Extract main title
            title = await page.title()
            print(f"[+] Page Title: {title}")
            
            # Take screenshot for visual validation
            os.makedirs("sandbox/outputs", exist_ok=True)
            screenshot_path = "sandbox/outputs/github_docs_communities.png"
            await page.screenshot(path=screenshot_path)
            print(f"[+] Screenshot saved to {screenshot_path}")
            
            # Extract links and headers in the community section
            headers = await page.locator("h2, h3").all_inner_texts()
            print("\n[+] Found Headers:")
            for h in headers[:15]:
                print(f"  - {h}")
                
            # Write to a log file
            log_path = "sandbox/outputs/github_docs_log.txt"
            with open(log_path, "w") as f:
                f.write(f"Source URL: {target_url}\n")
                f.write(f"Page Title: {title}\n\n")
                f.write("Headers found:\n")
                for h in headers:
                    f.write(f"- {h}\n")
            print(f"\n[+] Log successfully written to {log_path}")
            
        except Exception as e:
            print(f"[-] Error during navigation or extraction: {e}")
        finally:
            await browser.close()
            print("[*] Browser closed.")

if __name__ == "__main__":
    asyncio.run(explore_github())
