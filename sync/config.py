import os
import logging


class AppConfig:
    """Configuration class for modifying behaviour of  the crawler."""

    # Directories
    OUTPUT_FOLDER = (
        "output"  # The root dir where the results and reports of the app will be saved
    )
    FAILED_TASKS_FILE = os.path.join(OUTPUT_FOLDER, "failed_tasks.csv")

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)  # Ensure output folder exists

    # Logging Configuration
    SHOW_TRACEBACKS = False  # Set to False to hide detailed error logs
    LOG_FILE = os.path.join(OUTPUT_FOLDER, "crawler.log")
    LOG_LEVEL = logging.INFO  # Change to DEBUG if needed

    # Excel File Path
    EXCEL_FILE = os.path.join(OUTPUT_FOLDER, "apps_data.xlsx")

    # Playwright Settings
    HEADLESS_MODE = True  # Set to False for debugging
    LOG_MORE_COMMENTS_BUTTON_CLICKED = True  # Set to False for production
    REFRESH_NO_COMMENTS_PAGE_TIMEOUT = 30_000  # First time playwright load the page
    REFRESH_ALL_COMMENTS_PAGE_TIMEOUT = (
        360  # Timeout for clicking on all more comments buttons
    )

    # Fetch Service Settings
    FETCH_WITH_TIMEOUT = True  # Set to False for disabling fetch timout
    FETCH_METADATA_TIMEOUT = 30
    FETCH_APP_LINKS_TIMEOUT = 30
    FETCH_COMMENTS_TIMEOUT = 30

    # URLs
    MAIN_DOMAIN = "https://cafebazaar.ir"
    APP_ROUTE = "/lists/ml-mental-health-exercises"

    # Retry settings for requests
    MAX_RETRIES = 3
    REQUEST_TIMEOUT = 10

    @classmethod
    def log_config(cls):
        logging.info("🔧 Configuration loaded successfully:")


# **Initialize Logging** (Ensures logging is set up before main runs)
logging.basicConfig(
    filename=AppConfig.LOG_FILE,
    level=AppConfig.LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a",
)

# Also log to console
console_handler = logging.StreamHandler()
console_handler.setLevel(AppConfig.LOG_LEVEL)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logging.getLogger().addHandler(console_handler)

# Log all configurations on startup
AppConfig.log_config()
