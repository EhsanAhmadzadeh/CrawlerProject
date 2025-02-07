from utils import send_request, clean_text
from bs4 import BeautifulSoup
from typing import List, TypedDict, Optional
from playwright.async_api import async_playwright


class AppMetadata(TypedDict):
    installation_counts: str
    app_score: str
    app_category: str
    app_size: str
    app_last_update: str
    description_content: str
    app_name:str
    app_images: List[str]
    
    
class CommentMetadata(TypedDict):
    username: str
    account_id : str
    rating: int
    comment: str
    comment_date: str



def get_app_metadata(app_url: str) -> Optional[AppMetadata]:
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
        app_images = carousel_elements.find_all("source")
        app_images = [e.get("data-lazy-srcset") for e in app_images]

        keys = ("installation_counts", "app_score", "app_category", "app_size", "app_last_update")

        app_metadata: AppMetadata = {key: info_cubes_elements[i] for i, key in enumerate(keys)}
        app_metadata["app_name"] = app_name
        app_metadata["description_content"] = description_content
        app_metadata["app_images"] = app_images
        return app_metadata

    except Exception as error:
        print(f"Error occurred: {error}")
        return None


# # Test URL
# URL = "https://cafebazaar.ir/app/com.getsomeheadspace.android"

# print(get_app_metadata(URL))


    
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



# MAIN_DOMAIN = "https://cafebazaar.ir" 
# MENTAL_HEALTH_APP_ROUTE = "/lists/ml-mental-health-exercises"
    
# print(get_app_names(MAIN_DOMAIN+MENTAL_HEALTH_APP_ROUTE))    
    
    
def get_comments_data(page_html: str):
    try:
        soup = BeautifulSoup(page_html, "lxml")
        app_comments_divs = soup.find_all("div", "AppComment")

        comments_data = [
            {
                "username": div.find("div", class_="AppComment__username").text,
                "account_id": div.get("accountid"),
                "rating": int(div.find("div", class_="rating__fill").get("style").split(":")[1][:-2]) // 20,
                "comment": div.find("div", class_="AppComment__body").text.strip(),
                "comment_date": div.find("div", class_="AppComment__meta").find_next_sibling().text,
            }
            for div in app_comments_divs
        ]

        return comments_data

    except Exception as error:
        print(f"Error occurred: {error}")
        return None

    
    
# # Test URL
# URL = "https://cafebazaar.ir/app/com.getsomeheadspace.android"
# get_comments_data(URL)



async def get_all_comments_page_html(url: str) -> str:
    """
    Scrapes all comments from a JavaScript-heavy webpage using Playwright.
    
    :param url: The URL of the webpage.
    :return: The full HTML of the page after all comments have loaded.
    """
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
