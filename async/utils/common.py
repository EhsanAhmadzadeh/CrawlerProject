import unicodedata
import logging
import pandas as pd
import os
import traceback
from config import AppConfig

def clean_text(text: str) -> str:
    """
    Cleans unwanted Unicode characters and extra spaces from the text.
    """
    normalized_text = unicodedata.normalize("NFKC", text or "")
    cleaned_text = normalized_text.replace("\u200c", "").strip()
    return " ".join(cleaned_text.split())


def log_failed_task(url: str, error_type: str, error_message: str):
    """Logs a failed task to CSV and optionally prints traceback."""
    error_data = pd.DataFrame(
        [{"url": url, "error_type": error_type, "error_message": error_message}]
    )
    file_exists = os.path.exists(AppConfig.FAILED_TASKS_FILE)
    error_data.to_csv(
        AppConfig.FAILED_TASKS_FILE, mode="a", index=False, header=not file_exists
    )

    if AppConfig.SHOW_TRACEBACKS:
        logging.error(
            f"❌ {error_type} - {url}: {error_message}\n{traceback.format_exc()}"
        )
    else:
        logging.error(f"❌ {error_type} - {url}: {error_message}")
