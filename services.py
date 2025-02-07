from utils import send_request, clean_text
from bs4 import BeautifulSoup
from typing import List, TypedDict, Optional


class AppMetadata(TypedDict):
    installation_counts: str
    app_score: str
    app_category: str
    app_size: str
    app_last_update: str
    description_content: str
    app_name:str
    app_images: List[str]



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


# Test URL
URL = "https://cafebazaar.ir/app/com.getsomeheadspace.android"

print(get_app_metadata(URL))


    
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
    
    
    