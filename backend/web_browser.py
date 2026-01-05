from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from typing import Optional
from config import settings

class WebBrowser:
    """Handle web browsing and automation using Playwright"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
    async def initialize(self):
        """Initialize browser with a separate automation profile"""
        if not self.playwright:
            print("\n🌐 [Browser] Initializing Playwright...")
            import os
            self.playwright = await async_playwright().start()
            print("    ✅ Playwright started")
            
            # Use a separate profile directory for automation (won't conflict with your main Chrome)
            automation_profile = os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data - Automation')
            print(f"    Profile: {automation_profile}")
            print(f"    Headless: {settings.browser_headless}")
            print(f"    Persistent: {settings.browser_persistent}")
            
            try:
                print("    Launching Chrome with persistent context...")
                # Launch with persistent context using automation profile
                # Note: launch_persistent_context returns a BrowserContext, not Browser
                self.context = await self.playwright.chromium.launch_persistent_context(
                    automation_profile,
                    headless=settings.browser_headless,
                    channel="chrome",  # Use actual Chrome
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--exclude-switches=enable-automation',
                        '--disable-infobars',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                    ],
                    ignore_default_args=['--enable-automation']
                )
                
                # Get or create a page from the context
                print(f"    Existing pages: {len(self.context.pages)}")
                if len(self.context.pages) > 0:
                    self.page = self.context.pages[0]
                    print(f"    ✅ Using existing page")
                else:
                    self.page = await self.context.new_page()
                    print(f"    ✅ Created new page")
                
                # Remove webdriver detection
                await self.page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)
                print(f"    ✅ Webdriver detection removed")
                
                print(f"\n✅ Browser initialized successfully (Persistent: {settings.browser_persistent})")
                
            except Exception as e:
                print(f"❌ Browser initialization failed: {e}")
                # Fallback to regular browser without profile
                self.browser = await self.playwright.chromium.launch(
                    headless=settings.browser_headless,
                    channel="chrome"
                )
                self.context = await self.browser.new_context()
                self.page = await self.context.new_page()
            
    async def close(self):
        """Close browser"""
        print("\n🌐 [Browser] Close requested")
        
        # Check if browser should remain open
        if settings.browser_persistent:
            print("    ℹ️ Browser persistence enabled - keeping browser open")
            print("    Detaching from browser but NOT closing it")
            # Just clear references without closing
            self.page = None
            self.context = None
            self.browser = None
            self.playwright = None
            print("    ✅ Browser detached (still running)")
            return
        
        # Otherwise, close everything
        print("    Closing browser completely...")
        try:
            if self.page:
                print("    Closing page...")
                await self.page.close()
                self.page = None
            if self.context:
                print("    Closing context...")
                await self.context.close()
                self.context = None
            if self.browser:
                print("    Closing browser...")
                await self.browser.close()
                self.browser = None
            if self.playwright:
                print("    Stopping Playwright...")
                await self.playwright.stop()
                self.playwright = None
            print("    ✅ Browser closed completely")
        except Exception as e:
            print(f"    ⚠️ Browser close error: {e}")
            
    async def navigate(self, url: str) -> dict:
        """
        Navigate to URL
        
        Returns:
            {success: bool, title: str, url: str, error: str}
        """
        print(f"\n🌐 [Browser] Navigating to: {url}")
        try:
            await self.initialize()
            print(f"    Loading page (timeout: {settings.browser_timeout}ms)...")
            response = await self.page.goto(
                url,
                timeout=settings.browser_timeout,
                wait_until='networkidle'
            )
            
            title = await self.page.title()
            print(f"    ✅ Page loaded: {title}")
            print(f"    Status: {response.status if response else 'N/A'}")
            
            return {
                "success": True,
                "title": title,
                "url": self.page.url,
                "status": response.status if response else None
            }
        except Exception as e:
            print(f"    ❌ Navigation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_page_content(self) -> str:
        """Get page text content"""
        try:
            await self.initialize()
            return await self.page.inner_text('body')
        except Exception as e:
            return f"Error: {e}"
    
    async def get_page_html(self) -> str:
        """Get page HTML"""
        try:
            await self.initialize()
            return await self.page.content()
        except Exception as e:
            return f"Error: {e}"
    
    async def click_element(self, selector: str) -> dict:
        """Click an element by CSS selector"""
        try:
            await self.initialize()
            await self.page.click(selector, timeout=5000)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def type_text(self, selector: str, text: str) -> dict:
        """Type text into an element"""
        try:
            await self.initialize()
            await self.page.fill(selector, text)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def screenshot(self, full_page: bool = False) -> Optional[bytes]:
        """Take screenshot of current page"""
        try:
            await self.initialize()
            return await self.page.screenshot(full_page=full_page)
        except Exception as e:
            print(f"Screenshot error: {e}")
            return None
    
    async def execute_script(self, script: str) -> any:
        """Execute JavaScript on page"""
        try:
            await self.initialize()
            return await self.page.evaluate(script)
        except Exception as e:
            return f"Error: {e}"
    
    async def search_google(self, query: str) -> dict:
        """Perform a Google search"""
        try:
            await self.navigate(f"https://www.google.com/search?q={query}")
            
            # Get search results
            results = await self.page.query_selector_all('.g')
            search_results = []
            
            for result in results[:5]:  # Top 5 results
                try:
                    title_elem = await result.query_selector('h3')
                    link_elem = await result.query_selector('a')
                    
                    if title_elem and link_elem:
                        title = await title_elem.inner_text()
                        link = await link_elem.get_attribute('href')
                        search_results.append({"title": title, "url": link})
                except:
                    continue
            
            return {
                "success": True,
                "query": query,
                "results": search_results
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def scroll(self, direction: str = "down", amount: int = 500) -> dict:
        """Scroll the page"""
        print(f"🌐 [Browser] Scrolling {direction} by {amount}px")
        try:
            await self.initialize()
            if direction == "down":
                await self.page.evaluate(f"window.scrollBy(0, {amount})")
            elif direction == "up":
                await self.page.evaluate(f"window.scrollBy(0, -{amount})")
            elif direction == "bottom":
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            elif direction == "top":
                await self.page.evaluate("window.scrollTo(0, 0)")
            print(f"    ✅ Scrolled {direction}")
            return {"success": True}
        except Exception as e:
            print(f"    ❌ Scroll failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_links(self) -> dict:
        """Extract all links from the page"""
        print("🌐 [Browser] Extracting links...")
        try:
            await self.initialize()
            links = await self.page.evaluate("""() => {
                const anchors = Array.from(document.querySelectorAll('a'));
                return anchors.map(a => ({
                    text: a.innerText.trim(),
                    href: a.href,
                    title: a.title
                })).filter(link => link.href && link.href.startsWith('http'));
            }""")
            print(f"    ✅ Found {len(links)} links")
            return {"success": True, "links": links, "count": len(links)}
        except Exception as e:
            print(f"    ❌ Failed to extract links: {e}")
            return {"success": False, "error": str(e)}
    
    async def wait_for_selector(self, selector: str, timeout: int = 10000) -> dict:
        """Wait for an element to appear"""
        print(f"🌐 [Browser] Waiting for selector: {selector}")
        try:
            await self.initialize()
            await self.page.wait_for_selector(selector, timeout=timeout)
            print(f"    ✅ Element found")
            return {"success": True}
        except Exception as e:
            print(f"    ❌ Element not found: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_element_text(self, selector: str) -> dict:
        """Get text from specific element(s)"""
        print(f"🌐 [Browser] Getting text from: {selector}")
        try:
            await self.initialize()
            elements = await self.page.query_selector_all(selector)
            texts = []
            for elem in elements:
                text = await elem.inner_text()
                if text.strip():
                    texts.append(text.strip())
            print(f"    ✅ Found {len(texts)} element(s)")
            return {"success": True, "texts": texts, "count": len(texts)}
        except Exception as e:
            print(f"    ❌ Failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def click_text(self, text: str) -> dict:
        """Click an element containing specific text"""
        print(f"🌐 [Browser] Clicking element with text: '{text}'")
        try:
            await self.initialize()
            # Try to find and click element with matching text
            await self.page.click(f"text={text}", timeout=5000)
            print(f"    ✅ Clicked successfully")
            return {"success": True}
        except Exception as e:
            print(f"    ❌ Click failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_page_info(self) -> dict:
        """Get comprehensive page information"""
        print("🌐 [Browser] Getting page info...")
        try:
            await self.initialize()
            info = await self.page.evaluate("""() => {
                return {
                    title: document.title,
                    url: window.location.href,
                    domain: window.location.hostname,
                    protocol: window.location.protocol,
                    scrollHeight: document.body.scrollHeight,
                    scrollTop: window.pageYOffset,
                    viewportHeight: window.innerHeight,
                    viewportWidth: window.innerWidth,
                    linkCount: document.querySelectorAll('a').length,
                    imageCount: document.querySelectorAll('img').length,
                    formCount: document.querySelectorAll('form').length,
                    inputCount: document.querySelectorAll('input').length,
                    buttonCount: document.querySelectorAll('button').length
                };
            }""")
            print(f"    ✅ Page: {info['title']}")
            return {"success": True, **info}
        except Exception as e:
            print(f"    ❌ Failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def extract_structured_data(self) -> dict:
        """Extract structured content (headings, paragraphs, lists)"""
        print("🌐 [Browser] Extracting structured data...")
        try:
            await self.initialize()
            data = await self.page.evaluate("""() => {
                const headings = Array.from(document.querySelectorAll('h1, h2, h3'))
                    .map(h => ({ level: h.tagName, text: h.innerText.trim() }))
                    .filter(h => h.text);
                
                const paragraphs = Array.from(document.querySelectorAll('p'))
                    .map(p => p.innerText.trim())
                    .filter(p => p.length > 20); // Filter short paragraphs
                
                const lists = Array.from(document.querySelectorAll('ul li, ol li'))
                    .map(li => li.innerText.trim())
                    .filter(li => li);
                
                return { headings, paragraphs, lists };
            }""")
            print(f"    ✅ Extracted: {len(data['headings'])} headings, {len(data['paragraphs'])} paragraphs")
            return {"success": True, **data}
        except Exception as e:
            print(f"    ❌ Failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def fill_form(self, fields: dict) -> dict:
        """Fill multiple form fields at once
        
        Args:
            fields: Dict mapping selector to value, e.g. {"#email": "test@example.com"}
        """
        print(f"🌐 [Browser] Filling form with {len(fields)} field(s)")
        try:
            await self.initialize()
            results = []
            for selector, value in fields.items():
                try:
                    await self.page.fill(selector, str(value))
                    results.append({"selector": selector, "success": True})
                    print(f"    ✅ Filled: {selector}")
                except Exception as e:
                    results.append({"selector": selector, "success": False, "error": str(e)})
                    print(f"    ❌ Failed: {selector} - {e}")
            
            success_count = sum(1 for r in results if r["success"])
            print(f"    Completed: {success_count}/{len(fields)} fields")
            return {"success": True, "results": results}
        except Exception as e:
            print(f"    ❌ Failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def press_key(self, key: str) -> dict:
        """Press a keyboard key (Enter, Escape, Tab, etc)"""
        print(f"🌐 [Browser] Pressing key: {key}")
        try:
            await self.initialize()
            await self.page.keyboard.press(key)
            print(f"    ✅ Key pressed")
            return {"success": True}
        except Exception as e:
            print(f"    ❌ Failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def hover(self, selector: str) -> dict:
        """Hover over an element"""
        print(f"🌐 [Browser] Hovering over: {selector}")
        try:
            await self.initialize()
            await self.page.hover(selector)
            print(f"    ✅ Hovered")
            return {"success": True}
        except Exception as e:
            print(f"    ❌ Failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def select_option(self, selector: str, value: str) -> dict:
        """Select an option from a dropdown"""
        print(f"🌐 [Browser] Selecting '{value}' in: {selector}")
        try:
            await self.initialize()
            await self.page.select_option(selector, value)
            print(f"    ✅ Selected")
            return {"success": True}
        except Exception as e:
            print(f"    ❌ Failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_cookies(self) -> dict:
        """Get all cookies for current page"""
        print("🌐 [Browser] Getting cookies...")
        try:
            await self.initialize()
            cookies = await self.context.cookies()
            print(f"    ✅ Found {len(cookies)} cookie(s)")
            return {"success": True, "cookies": cookies, "count": len(cookies)}
        except Exception as e:
            print(f"    ❌ Failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def new_tab(self, url: Optional[str] = None) -> dict:
        """Open a new tab"""
        print(f"🌐 [Browser] Opening new tab{f' to {url}' if url else ''}")
        try:
            await self.initialize()
            new_page = await self.context.new_page()
            if url:
                await new_page.goto(url)
            # Switch to new page
            self.page = new_page
            print(f"    ✅ New tab opened")
            return {"success": True, "url": self.page.url if url else "about:blank"}
        except Exception as e:
            print(f"    ❌ Failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def list_tabs(self) -> dict:
        """List all open tabs"""
        print("🌐 [Browser] Listing tabs...")
        try:
            await self.initialize()
            pages = self.context.pages
            tabs = []
            for i, page in enumerate(pages):
                tabs.append({
                    "index": i,
                    "title": await page.title(),
                    "url": page.url,
                    "is_current": page == self.page
                })
            print(f"    ✅ Found {len(tabs)} tab(s)")
            return {"success": True, "tabs": tabs, "count": len(tabs)}
        except Exception as e:
            print(f"    ❌ Failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def switch_tab(self, index: int) -> dict:
        """Switch to a different tab by index"""
        print(f"🌐 [Browser] Switching to tab {index}")
        try:
            await self.initialize()
            pages = self.context.pages
            if 0 <= index < len(pages):
                self.page = pages[index]
                title = await self.page.title()
                print(f"    ✅ Switched to: {title}")
                return {"success": True, "title": title, "url": self.page.url}
            else:
                print(f"    ❌ Invalid index")
                return {"success": False, "error": f"Tab index {index} out of range (0-{len(pages)-1})"}
        except Exception as e:
            print(f"    ❌ Failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def close_tab(self, index: Optional[int] = None) -> dict:
        """Close a tab (current tab if index not specified)"""
        print(f"🌐 [Browser] Closing tab{f' {index}' if index is not None else ''}")
        try:
            await self.initialize()
            pages = self.context.pages
            
            if len(pages) <= 1:
                print(f"    ❌ Cannot close last tab")
                return {"success": False, "error": "Cannot close the last tab"}
            
            if index is not None:
                if 0 <= index < len(pages):
                    await pages[index].close()
                    # Switch to first remaining tab
                    self.page = self.context.pages[0]
                else:
                    return {"success": False, "error": f"Invalid index {index}"}
            else:
                await self.page.close()
                self.page = self.context.pages[0]
            
            print(f"    ✅ Tab closed")
            return {"success": True, "remaining_tabs": len(self.context.pages)}
        except Exception as e:
            print(f"    ❌ Failed: {e}")
            return {"success": False, "error": str(e)}

# Global instance
web_browser = WebBrowser()
