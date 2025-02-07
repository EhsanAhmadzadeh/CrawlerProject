import asyncio
from playwright.async_api import async_playwright
from typing import List


async def get_all_comments(url: str) -> List[str]:
    """
    Scrapes all comments from a JavaScript-heavy webpage using Playwright.
    
    :param url: The URL of the webpage.
    :return: A list of extracted comments.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set headless=False for debugging
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

        # Extract all comments
        comments_elements = await page.query_selector_all(".CommentText")  # Replace with actual comment class
        comments = [await comment.inner_text() for comment in comments_elements]

        await browser.close()
        return comments


# Test the function
url = "https://cafebazaar.ir/app/com.getsomeheadspace.android"

# Run Playwright async function
comments = asyncio.run(get_all_comments(url))

# Print collected comments
for idx, comment in enumerate(comments, start=1):
    print(f"{idx}. {comment}")
