import concurrent.futures
import logging
import uuid
from bs4 import BeautifulSoup
from utils import send_request, clean_text
from typing import List, TypedDict, Optional
from config import AppConfig


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


def run_with_timeout(func, *args, timeout=60):
    """Runs a function with a timeout using ThreadPoolExecutor."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(func, *args)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            logging.error(f"❌ Timeout: {func.__name__} took longer than {timeout}s")
            raise TimeoutError(f"{func.__name__} exceeded {timeout}s timeout")


def get_app_metadata(app_url: str) -> Optional[AppMetadata]:
    """Fetches app metadata with timeout."""
    try:
        response = (
            run_with_timeout(
                send_request, app_url, timeout=AppConfig.FETCH_METADATA_TIMEOUT
            )
            if AppConfig.FETCH_WITH_TIMEOUT
            else send_request(app_url)
        )
        soup = BeautifulSoup(response.text, "lxml")

        detail_page_header = soup.find("section", class_="DetailsPageHeader")
        app_name = detail_page_header.find("h1", class_="AppName").text

        info_cubes_table = detail_page_header.find_all("td", class_="InfoCube__content")
        info_cubes_elements = [clean_text(e.text) for e in info_cubes_table]

        description_content = clean_text(
            soup.find("div", class_="AppDescriptionContent").text
        )
        carousel_elements = soup.find("div", class_="carousel__inner-content")
        app_images = [
            e.get("data-lazy-srcset") for e in carousel_elements.find_all("source")
        ]

        app_metadata: AppMetadata = {
            "app_id": int(uuid.uuid4().int % (10**8)),
            "app_name": app_name,
            "description_content": description_content,
            "installation_counts": info_cubes_elements[0],
            "app_score": info_cubes_elements[1],
            "app_category": info_cubes_elements[2],
            "app_size": info_cubes_elements[3],
            "app_last_update": info_cubes_elements[4],
            "app_images": app_images,
        }
        return app_metadata

    except Exception as error:
        logging.error(f"Error fetching app metadata: {error}")
        return None  # Skip this app


def get_app_links(url: str):
    """Fetches app links with timeout."""
    try:
        response = (
            run_with_timeout(
                send_request, url, timeout=AppConfig.FETCH_APP_LINKS_TIMEOUT
            )
            if AppConfig.FETCH_WITH_TIMEOUT
            else send_request(url)
        )
        soup = BeautifulSoup(response.text, "lxml")
        titles = soup.find_all("a", "SimpleAppItem SimpleAppItem--single")
        return [title.get("href") for title in titles]

    except Exception as error:
        logging.error(f"Error fetching app links: {error}")
        return []


def get_comments_data(page_html: str, app_id: int) -> List[CommentMetadata]:
    """Extracts comments from the HTML with timeout."""
    try:
        return (
            run_with_timeout(
                _extract_comments,
                page_html,
                app_id,
                timeout=AppConfig.FETCH_COMMENTS_TIMEOUT,
            )
            if AppConfig.FETCH_WITH_TIMEOUT
            else _extract_comments(page_html, app_id)
        )
    except Exception as error:
        logging.error(f"Error extracting comments: {error}")
        return []  # Skip comments if failed


def _extract_comments(page_html: str, app_id: int) -> List[CommentMetadata]:
    """Helper function to extract comments without timeout handling."""
    soup = BeautifulSoup(page_html, "lxml")
    app_comments_divs = soup.find_all("div", "AppComment")

    return [
        {
            "comment_id": int(
                uuid.uuid4().int % (10**8)
            ),  # Generate 8-digit unique comment ID
            "app_id": app_id,  # Foreign key linking to app
            "username": div.find("div", class_="AppComment__username").text,
            "account_id": div.get("accountid"),
            "rating": int(
                div.find("div", class_="rating__fill").get("style").split(":")[1][:-2]
            )
            // 20,
            "comment": div.find("div", class_="AppComment__body").text.strip(),
            "comment_date": div.find("div", class_="AppComment__rating")
            .find_next_sibling()
            .text,
        }
        for div in app_comments_divs
    ]
