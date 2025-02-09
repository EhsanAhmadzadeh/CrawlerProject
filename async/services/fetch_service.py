import logging
import uuid
from typing import List, Optional, TypedDict
from bs4 import BeautifulSoup
from config import AppConfig
from utils.http_client import async_send_request
from utils.common import clean_text
import asyncio


class AppMetadata(TypedDict):
    app_id: int
    installation_counts: str
    app_score: str
    app_category: str
    app_size: str
    app_last_update: str
    description_content: str
    app_name: str
    app_images: List[str]


class CommentMetadata(TypedDict):
    comment_id: int
    username: str
    account_id: str
    rating: int
    comment: str
    comment_date: str
    app_id: int


async def get_app_links(url: str) -> List[str]:
    """
    Fetches app links from a listing page.
    """
    logging.info(f"🔗 Fetching app links from {url}")

    if AppConfig.FETCH_WITH_TIMEOUT:
        try:
            # Use asyncio.wait_for to impose an overall time limit
            response_data = await asyncio.wait_for(
                async_send_request(url),
                timeout=AppConfig.FETCH_APP_LINKS_TIMEOUT
            )
        except asyncio.TimeoutError:
            logging.error(f"❌ Timeout while fetching links from {url}")
            return []
    else:
        response_data = await async_send_request(url)

    if "error" in response_data:
        logging.error(response_data["error"])
        return []

    soup = BeautifulSoup(response_data["text"], "lxml")
    titles = soup.find_all("a", "SimpleAppItem SimpleAppItem--single")
    return [title.get("href") for title in titles if title.get("href")]


async def get_app_metadata(app_url: str) -> Optional[AppMetadata]:
    """
    Fetches and parses app metadata from the app detail page.
    """
    logging.info(f"🔍 Fetching metadata for {app_url}")

    # Optionally wrap with asyncio.wait_for to impose total time limit
    if AppConfig.FETCH_WITH_TIMEOUT:
        try:
            response_data = await asyncio.wait_for(
                async_send_request(app_url),
                timeout=AppConfig.FETCH_METADATA_TIMEOUT
            )
        except asyncio.TimeoutError:
            logging.error(f"❌ Timeout while fetching metadata from {app_url}")
            return None
    else:
        response_data = await async_send_request(app_url)

    if "error" in response_data:
        logging.error(f"Error in response: {response_data['error']}")
        return None

    try:
        soup = BeautifulSoup(response_data["text"], "lxml")
        detail_page_header = soup.find("section", class_="DetailsPageHeader")
        if not detail_page_header:
            raise ValueError("Could not find DetailsPageHeader section.")

        app_name_el = detail_page_header.find("h1", class_="AppName")
        if not app_name_el:
            raise ValueError("Could not find AppName in header.")

        app_name = clean_text(app_name_el.text)

        info_cubes_table = detail_page_header.find_all("td", class_="InfoCube__content")
        info_cubes = [clean_text(e.text) for e in info_cubes_table]

        description_div = soup.find("div", class_="AppDescriptionContent")
        description_content = clean_text(description_div.text if description_div else "")

        carousel_elements = soup.find("div", class_="carousel__inner-content")
        if carousel_elements:
            app_images = [
                e.get("data-lazy-srcset") for e in carousel_elements.find_all("source")
                if e.get("data-lazy-srcset")
            ]
        else:
            app_images = []

        # Example: we expect info_cubes[0..4] to exist
        # But always check length to avoid IndexError
        metadata = AppMetadata({
            "app_id": int(uuid.uuid4().int % (10**8)),
            "app_name": app_name,
            "description_content": description_content,
            "installation_counts": info_cubes[0] if len(info_cubes) > 0 else "",
            "app_score": info_cubes[1] if len(info_cubes) > 1 else "",
            "app_category": info_cubes[2] if len(info_cubes) > 2 else "",
            "app_size": info_cubes[3] if len(info_cubes) > 3 else "",
            "app_last_update": info_cubes[4] if len(info_cubes) > 4 else "",
            "app_images": app_images,
        })
        return metadata

    except Exception as error:
        logging.error(f"Error parsing metadata: {error}")
        return None


def extract_comments(page_html: str, app_id: int) -> List[CommentMetadata]:
    """
    Extracts comments from a full HTML string (already loaded by Playwright).
    Synchronous parse is generally fast; if large, consider offloading with to_thread.
    """
    soup = BeautifulSoup(page_html, "lxml")
    app_comments_divs = soup.find_all("div", "AppComment")

    comments = []
    for div in app_comments_divs:
        username_el = div.find("div", class_="AppComment__username")
        rating_el = div.find("div", class_="rating__fill")
        body_el = div.find("div", class_="AppComment__body")
        date_el = div.find("div", class_="AppComment__rating")
        date_el = date_el.find_next_sibling() if date_el else None

        # rating style is something like "width:80%"
        rating = 0
        if rating_el and rating_el.get("style"):
            style_val = rating_el.get("style")  # e.g. "width:80%"
            num_str = style_val.split(":")[1][:-2]  # "80"
            rating = int(num_str) // 20  # 80 -> 4 star

        comment_data = CommentMetadata({
            "comment_id": int(uuid.uuid4().int % (10**8)),
            "app_id": app_id,
            "username": clean_text(username_el.text if username_el else ""),
            "account_id": div.get("accountid", ""),
            "rating": rating,
            "comment": clean_text(body_el.text if body_el else ""),
            "comment_date": clean_text(date_el.text if date_el else ""),
        })
        comments.append(comment_data)
    return comments
