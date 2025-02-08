import logging
import pandas as pd
import asyncio
from config import AppConfig
from services.fetch_service import (
    get_app_metadata,
    get_app_links,
    extract_comments,
)
from services.playwright_service import fetch_comments_full_page_with_timeout
from services.io_service import write_to_excel, create_excel_if_not_exists
from utils.common import log_failed_task


async def process_app(full_url: str):
    """
    Processes each app: fetch metadata, fetch comments HTML (via Playwright),
    parse comments, and persist results.
    """
    # 1) Fetch App Metadata
    try:
        app_metadata = await get_app_metadata(full_url)
        if not app_metadata:
            raise ValueError("Metadata extraction returned None/empty.")
    except asyncio.TimeoutError:
        log_failed_task(full_url, "Metadata Timeout", "Metadata fetch exceeded timeout.")
        logging.warning(f"⚠️ Skipping app due to metadata timeout: {full_url}")
        return
    except Exception as e:
        log_failed_task(full_url, "Metadata Error", str(e))
        logging.warning(f"⚠️ Skipping app due to metadata failure: {full_url}")
        return

    logging.info(f"✅ App metadata fetched: {app_metadata.get('app_name')} (ID: {app_metadata.get('app_id')})")

    # 2) Fetch Full Page HTML with Comments (Playwright)
    try:
        page_html = await fetch_comments_full_page_with_timeout(full_url)
    except TimeoutError:
        log_failed_task(full_url, "Comment Timeout", "Comment fetch exceeded timeout.")
        logging.warning(f"⚠️ Skipping app due to comment timeout: {full_url}")
        return
    except Exception as e:
        log_failed_task(full_url, "Comment Error", str(e))
        logging.warning(f"⚠️ Skipping app due to comment failure: {full_url}")
        return

    # 3) Parse Comments (BeautifulSoup)
    try:
        comments = extract_comments(page_html, app_metadata["app_id"])
    except Exception as e:
        log_failed_task(full_url, "Comment Parsing Error", str(e))
        logging.warning(f"⚠️ Skipping app due to comment parsing failure: {full_url}")
        return

    logging.info(f"💬 Fetched {len(comments)} comments for {app_metadata['app_name']}")

    # 4) Write to Excel
    app_df = pd.DataFrame([app_metadata])
    comments_df = pd.DataFrame(comments)
    write_to_excel(app_df, comments_df)

    logging.info(f"📂 Data saved successfully for: {app_metadata['app_name']}")
    logging.info("------------------------------------------------------------")


async def main():
    """Main function that runs the crawler."""
    create_excel_if_not_exists()

    # 1) Get all the app links
    listing_url = AppConfig.MAIN_DOMAIN + AppConfig.APP_ROUTE
    links = await get_app_links(listing_url)
    logging.info(f"🔗 Found {len(links)} apps to process.")

    # 2) Process them in parallel (gather). For large sets, consider concurrency limits (semaphore).
    tasks = [process_app(AppConfig.MAIN_DOMAIN + link) for link in links]
    await asyncio.gather(*tasks)

    logging.info("✅ All apps processed successfully!")


if __name__ == "__main__":
    try:
        logging.info("🚀 Starting Crawler...")
        asyncio.run(main())
    except Exception as e:
        logging.error(f"❌ An error occurred in main: {e}")
