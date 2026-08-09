# Autonomous Web Raider Doctrine

## Sovereign Scraper Principles (No API Keys)
The Web Raider module embodies our principle of absolute technological sovereignty. It operates without reliance on external, paid scraping APIs or third-party web access services (such as OpenAI or Anthropic proxies). The agent interacts directly with web resources from the local host, preserving privacy and independence.

## Playwright Local Orchestration
Automation is orchestrated using `Playwright` asynchronously. The script drives a local headless or headful browser instance, handles complex web interactions (such as JS rendering, form submissions, and cookie prompts), and retrieves raw, semantic page content directly from the DOM.

## Multimodal Result Validation
To guarantee data integrity and bypass brittle selector dependencies:
1. The scraper generates automated screenshots of the target page at critical phases.
2. The agent uses its own multimodal capabilities to analyze and validate the screenshots visually, checking if the layout loaded correctly and confirming that the correct data was extracted.

To run the demonstration script:
```bash
python 04-Web-Raider/examples/scrape_demo.py
```
*Make sure to install playwright dependencies and drivers via `playwright install` beforehand.*
