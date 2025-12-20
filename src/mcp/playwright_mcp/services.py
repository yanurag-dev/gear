from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from typing import Optional, Dict, Any

class PlaywrightService:
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def start(self, headless: bool = False):
        if not self.playwright:
            self.playwright = sync_playwright().start()
        if not self.browser:
            self.browser = self.playwright.chromium.launch(headless=headless)
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            print("Browser started.")

    def stop(self):
        try:
            if self.page:
                self.page.close()
        except Exception:
            pass
        try:
            if self.context:
                self.context.close()
        except Exception:
            pass
        try:
            if self.browser:
                self.browser.close()
        except Exception:
            pass
        try:
            if self.playwright:
                self.playwright.stop()
        except Exception:
            pass
        
        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None
        print("Browser stopped.")

    def navigate(self, url: str):
        if not self.page:
            self.start()
        print(f"Navigating to {url}...")
        self.page.goto(url)

    def type(self, selector: str, text: str):
        if not self.page:
            raise RuntimeError("Browser not started. Call navigate first.")
        print(f"Typing '{text}' into '{selector}'...")
        self.page.fill(selector, text)

    def click(self, selector: str):
        if not self.page:
            raise RuntimeError("Browser not started. Call navigate first.")
        print(f"Clicking '{selector}'...")
        self.page.click(selector)

    def scrape(self, url: str = None) -> str:
        if url and self.page and self.page.url != url:
             self.navigate(url)
        
        if not self.page:
             raise RuntimeError("Browser not started.")

        print(f"Scraping content from {self.page.url}...")
        return self.page.content()

    def screenshot(self, path: str):
        if not self.page:
            raise RuntimeError("Browser not started.")
        self.page.screenshot(path=path)
