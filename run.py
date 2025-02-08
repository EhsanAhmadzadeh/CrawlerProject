import logging
import pandas as pd
from config import AppConfig
from services.fetch_service import get_app_metadata, get_comments_data, get_app_links
from services.playwright_service import fetch_comments_full_page_with_timeout
from services.io_service import write_to_excel, create_excel_if_not_exists
from utils import log_failed_task
import asyncio


async def process_app(full_url):
    """Processes each app, fetches metadata, comments, and logs failures."""

    logging.info(f"🔍 Fetching metadata for: {full_url}")

    try:
        app_metadata = await asyncio.wait_for(
            asyncio.to_thread(get_app_metadata, full_url),
            timeout=AppConfig.FETCH_METADATA_TIMEOUT,
        )
        if not app_metadata:
            raise ValueError("Metadata extraction failed (App metadata is empty).")
    except asyncio.TimeoutError:
        log_failed_task(
            full_url, "Metadata Timeout", "Metadata fetch exceeded timeout."
        )
        logging.warning(f"⚠️ Skipping app due to metadata timeout: {full_url}")
        return
    except Exception as e:
        log_failed_task(full_url, "Metadata Error", str(e))
        logging.warning(f"⚠️ Skipping app due to metadata failure: {full_url}")
        return

    logging.info(
        f"✅ App metadata fetched: {app_metadata['app_name']} (ID: {app_metadata['app_id']})"
    )

    logging.info(f"🔄 Scraping comments for {app_metadata['app_name']}...")

    try:
        page_html = await fetch_comments_full_page_with_timeout(full_url)
        comments = await asyncio.wait_for(
            asyncio.to_thread(get_comments_data, page_html, app_metadata["app_id"]),
            timeout=AppConfig.FETCH_COMMENTS_TIMEOUT,
        )
    except asyncio.TimeoutError:
        log_failed_task(full_url, "Comment Timeout", "Comment fetch exceeded timeout.")
        logging.warning(f"⚠️ Skipping app due to comment timeout: {full_url}")
        return
    except Exception as e:
        log_failed_task(full_url, "Comment Error", str(e))
        logging.warning(f"⚠️ Skipping app due to comment failure: {full_url}")
        return

    logging.info(f"💬 Fetched {len(comments)} comments for {app_metadata['app_name']}")

    # Store Data
    app_df = pd.DataFrame([app_metadata])
    comments_df = pd.DataFrame(comments)
    write_to_excel(app_df, comments_df)

    logging.info(f"📂 Data saved successfully for: {app_metadata['app_name']}")
    logging.info("------------------------------------------------------------")


async def main():
    """Main function that runs the crawler and logs failed tasks."""
    create_excel_if_not_exists()

    links = get_app_links(AppConfig.MAIN_DOMAIN + AppConfig.APP_ROUTE)
    logging.info(f"🔗 Found {len(links)} apps to process")

    for link in links:
        full_url = AppConfig.MAIN_DOMAIN + link
        result = await process_app(full_url)
        if result is None:
            continue  # skip the current iteration if error

    logging.info("✅ All apps processed successfully!")


if __name__ == "__main__":
    try:
        logging.info("🚀 Starting Crawler...")
        asyncio.run(main())
    except Exception as e:
        logging.error(f"❌ An error occurred: {e}")
