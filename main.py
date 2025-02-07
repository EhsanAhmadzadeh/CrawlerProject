from services import get_app_links, get_app_metadata



def main():

    MAIN_DOMAIN = "https://cafebazaar.ir" 
    MENTAL_HEALTH_APP_ROUTE = "/lists/ml-mental-health-exercises"
    
    links = get_app_links(MAIN_DOMAIN+MENTAL_HEALTH_APP_ROUTE)
    
    for link in links:
        print(get_app_metadata(MAIN_DOMAIN+link),"\n")
    
    
main()