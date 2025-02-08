from utils import send_request, clean_text
from bs4 import BeautifulSoup
from typing import List, TypedDict, Optional
from playwright.async_api import async_playwright
import uuid  # For generating unique IDs

# Define structured interfaces
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
    app_id: int  # Foreign Key linking comment to the app


def get_app_metadata(app_url: str) -> Optional[AppMetadata]:
    """Fetches app metadata and assigns a unique app_id."""
    response = send_request(app_url)
    try:
        soup = BeautifulSoup(response.text, "lxml")

        detail_page_header = soup.find("section", class_="DetailsPageHeader")
        app_name = detail_page_header.find("h1", class_="AppName").text

        info_cubes_table: List[BeautifulSoup] = detail_page_header.find_all("td", class_="InfoCube__content")
        info_cubes_elements: List[str] = [clean_text(e.text) for e in info_cubes_table]

        # Extract app description and clean it
        description_content = clean_text(soup.find("div", class_="AppDescriptionContent").text)
                
        carousel_elements = soup.find("div", class_="carousel__inner-content")
        app_images = [e.get("data-lazy-srcset") for e in carousel_elements.find_all("source")]

        keys = ("installation_counts", "app_score", "app_category", "app_size", "app_last_update")

        # Assign a unique app ID
        app_id = int(uuid.uuid4().int % (10**8))  # Generate an 8-digit unique int ID

        app_metadata: AppMetadata = {
            "app_id": app_id,
            "app_name": app_name,
            "description_content": description_content,
            "installation_counts": info_cubes_elements[0],
            "app_score": info_cubes_elements[1],
            "app_category": info_cubes_elements[2],
            "app_size": info_cubes_elements[3],
            "app_last_update": info_cubes_elements[4],
            "app_images": app_images
        }
        return app_metadata

    except Exception as error:
        print(f"Error occurred while fetching app metadata: {error}")
        return None


def get_comments_data(page_html: str, app_id: int) -> List[CommentMetadata]:
    """Extracts all comments from the HTML and links them to an app_id."""
    try:
        soup = BeautifulSoup(page_html, "lxml")
        app_comments_divs = soup.find_all("div", "AppComment")

        comments_data: List[CommentMetadata] = [
            {
                "comment_id": int(uuid.uuid4().int % (10**8)),  # Generate 8-digit unique comment ID
                "app_id": app_id,  # Foreign key linking to app
                "username": div.find("div", class_="AppComment__username").text,
                "account_id": div.get("accountid"),
                "rating": int(div.find("div", class_="rating__fill").get("style").split(":")[1][:-2]) // 20,
                "comment": div.find("div", class_="AppComment__body").text.strip(),
                "comment_date": div.find("div", class_="AppComment__rating").find_next_sibling().text,
            }
            for div in app_comments_divs
        ]

        return comments_data

    except Exception as error:
        print(f"Error occurred while extracting comments: {error}")
        return []


async def get_all_comments_page_html(url: str) -> str:
    """Scrapes all comments from a JavaScript-heavy webpage using Playwright."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Set to True for production
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


def get_app_links(url: str):
    response = send_request(url)
    try:
        soup = BeautifulSoup(response.text , "lxml")

        titles = soup.find_all("a","SimpleAppItem SimpleAppItem--single")
        app_links = [title.get("href") for title in titles]
        
        return app_links
        
    except Exception as error:
        print(f"Error occurred: {error}")
        return
