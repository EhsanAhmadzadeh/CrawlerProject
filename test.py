import asyncio
from playwright.async_api import async_playwright

async def get_all_comments_page_html(url: str) -> str:
    """
    Scrapes all comments from a JavaScript-heavy webpage using Playwright.
    
    :param url: The URL of the webpage.
    :return: The full HTML of the page after all comments have loaded.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set to True for production
        page = await browser.new_page()
        
        # Go to the page
        await page.goto(url, timeout=60000)  # 60-second timeout

        # Keep clicking "Load More Comments" until it disappears
        while True:
            try:
                load_more_button = await page.query_selector("span:text('نظرات بیشتر')")
                if load_more_button:
                    await load_more_button.click()
                    await page.wait_for_timeout(2000)  # Wait for new comments to load
                else:
                    break  # Button is gone, exit loop
            except Exception as e:
                print(f"Error clicking button: {e}")
                break  # If button not found, break the loop

        # Once the button disappears, get the full page HTML
        full_html = await page.content()

        await browser.close()
        return full_html


# Test the function
url = "https://cafebazaar.ir/app/com.getsomeheadspace.android"

# Run Playwright async function
page_html = asyncio.run(get_all_comments_page_html(url))

# Print or save the collected HTML
print(page_html)  # Print only the first 1000 characters for preview
