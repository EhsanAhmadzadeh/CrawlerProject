import logging
import asyncio
import traceback
from playwright.async_api import async_playwright
from config import AppConfig


async def fetch_comments_full_page_with_timeout(url: str) -> str:
    """Enforces a timeout for fetching the full comments page via Playwright."""
    try:
        return await asyncio.wait_for(
            get_page_w_all_comments_html(url),
            timeout=AppConfig.REFRESH_ALL_COMMENTS_PAGE_TIMEOUT,
        )
    except asyncio.TimeoutError as e:
        logging.error(f"❌ Timeout: Skipping comments for {url}")
        raise TimeoutError(e)


async def get_page_w_all_comments_html(url: str) -> str:
    """Scrolls & clicks 'more comments' until exhausted, then returns full HTML."""
    logging.info(f"🔄 Opening {url} to scrape all comments...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=AppConfig.HEADLESS_MODE)
        page = await browser.new_page()

        full_html = ""
        try:
            # NOTE: Page timeouts in playwright are in milliseconds
            await page.goto(url, timeout=AppConfig.REFRESH_NO_COMMENTS_PAGE_TIMEOUT)
            logging.info("✅ Page loaded successfully.")

            while True:
                load_more_button = await page.query_selector(
                    "button.newbtn.AppCommentsList__loadmore"
                )
                if load_more_button:
                    await load_more_button.click()
                    if AppConfig.LOG_MORE_COMMENTS_BUTTON_CLICKED:
                        logging.info("🔄 Clicked on more comments button ...")
                    # Let new comments load
                    await page.wait_for_timeout(2000)
                    # Scroll to bottom
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(1)
                else:
                    break

            full_html = await page.content()
            logging.info("📥 Successfully extracted page HTML.")

        except Exception as e:
            logging.error(f"❌ Playwright Error on {url}: {e}")
            if AppConfig.SHOW_TRACEBACKS:
                logging.error(traceback.format_exc())
        finally:
            await browser.close()

        return full_html
