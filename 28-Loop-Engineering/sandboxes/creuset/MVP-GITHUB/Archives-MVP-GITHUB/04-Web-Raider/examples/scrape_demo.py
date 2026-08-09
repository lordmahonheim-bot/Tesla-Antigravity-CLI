#!/usr/bin/env python3
"""
04-Web-Raider: Playwright Automation Demo
Autonomous semantic scraping demonstration without third-party API keys
"""
import asyncio
import os
import sys

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("[-] Playwright not installed. Run: pip install playwright")
    sys.exit(1)

async def main():
    print("[*] Running autonomous crawler...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "https://example.com"
        print(f"[*] Navigating to: {url}")
        await page.goto(url)
        
        title = await page.title()
        print(f"[+] Page title detected: {title}")
        
        content = await page.locator("body").inner_text()
        print("--- EXTRACTED CONTENT ---")
        print(content.strip())
        print("-------------------------")
        
        screenshot_path = os.environ.get("RAIDER_SCREENSHOT_PATH", "screenshot_demo.png")
        await page.screenshot(path=screenshot_path)
        print(f"[✓] Validation screenshot saved to: {screenshot_path}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
