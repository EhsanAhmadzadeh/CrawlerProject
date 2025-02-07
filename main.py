from services import get_app_links, get_app_metadata, get_all_comments_page_html, get_comments_data
import asyncio

MAIN_DOMAIN = "https://cafebazaar.ir" 
MENTAL_HEALTH_APP_ROUTE = "/lists/ml-mental-health-exercises"

async def main():
    # Get app links
    links = get_app_links(MAIN_DOMAIN + MENTAL_HEALTH_APP_ROUTE)
    
    for link in links:
        full_url = MAIN_DOMAIN + link  # Ensure full URL
        
        # Get metadata
        print(get_app_metadata(full_url), "\n")
        
        # Get all comments (Run Playwright async function)
        page_html = await get_all_comments_page_html(full_url)  # ✅ Get full HTML
        
        # Extract comments directly from HTML
        comments = get_comments_data(page_html)  # ✅ Pass HTML instead of URL
        print(comments)
        print("========================================================")

# Run the main function properly
asyncio.run(main())  # ✅ Use asyncio.run() ONCE
