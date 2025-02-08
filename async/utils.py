import httpx
import logging
import pandas as pd
import os
import traceback
from config import AppConfig

def clean_text(text: str) -> str:
    """Cleans unwanted characters and extra spaces from text."""
    return " ".join(text.strip().split()) if text else "N/A"

async def send_request(url: str) -> str:
    """Sends an async HTTP GET request with retries."""
    async with httpx.AsyncClient(timeout=AppConfig.HTTP_TIMEOUT) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as e:
            logging.error(f"❌ HTTP Error {e.response.status_code} for {url}")
        except httpx.RequestError as e:
            logging.error(f"❌ Request Error for {url}: {e}")
    return ""

def log_failed_task(url: str, error_type: str, error_message: str):
    """Logs a failed task to CSV and optionally includes tracebacks."""
    error_data = pd.DataFrame([{"url": url, "error_type": error_type, "error_message": error_message}])
    file_exists = os.path.exists(AppConfig.FAILED_TASKS_FILE)
    error_data.to_csv(AppConfig.FAILED_TASKS_FILE, mode="a", index=False, header=not file_exists)

    if AppConfig.SHOW_TRACEBACKS:
        logging.error(f"❌ {error_type} - {url}: {error_message}\n{traceback.format_exc()}")
    else:
        logging.error(f"❌ {error_type} - {url}: {error_message}")
