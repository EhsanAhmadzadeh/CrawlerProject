import requests
from requests.exceptions import RequestException, HTTPError, Timeout, ConnectionError
from typing import Dict, Optional, Union
import unicodedata
from config import AppConfig
import logging
import pandas as pd
import os
import traceback


def send_request(
    url: str,
    method: str = "GET",
    params: Optional[Dict[str, str]] = None,
    data: Optional[Dict[str, Union[str, int]]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 10,
    retries: int = 3,
) -> Dict[str, Union[int, str, Dict]]:
    """
    Sends an HTTP request with proper error handling and retry logic.

    :param url: The target URL.
    :param method: HTTP method ('GET' or 'POST').
    :param params: Dictionary of URL parameters (for GET requests).
    :param data: Dictionary of form data (for POST requests).
    :param headers: Dictionary of custom headers.
    :param timeout: Timeout for the request in seconds (default: 10).
    :param retries: Number of retry attempts on failure (default: 3).

    :return: A dictionary containing either the response data or an error message.
    """

    session = requests.Session()
    session.headers.update(headers or {})

    for attempt in range(retries):
        try:
            response: requests.Response

            if method.upper() == "GET":
                response = session.get(url, params=params, timeout=timeout)
            elif method.upper() == "POST":
                response = session.post(url, data=data, timeout=timeout)
            else:
                return {"error": f"Unsupported HTTP method: {method}"}

            # Raise an exception for HTTP error responses (4xx, 5xx)
            response.raise_for_status()

            # Try parsing JSON response, otherwise return plain text
            return response

        except HTTPError as http_err:
            return {"error": f"HTTP error occurred: {http_err}"}
        except ConnectionError:
            print(f"Connection error. Retrying {attempt + 1}/{retries}...")
        except Timeout:
            print(f"Request timed out. Retrying {attempt + 1}/{retries}...")
        except RequestException as req_err:
            return {"error": f"Request failed: {req_err}"}

    return {"error": "Request failed after multiple attempts"}


def clean_text(text: str) -> str:
    """
    Cleans unwanted Unicode characters and extra spaces from the text.
    """
    # Normalize Unicode (NFKC = compatibility decomposition)
    normalized_text = unicodedata.normalize("NFKC", text)

    # Remove Zero-Width Non-Joiner (\u200c) and other non-printable characters
    cleaned_text = normalized_text.replace("\u200c", "").strip()

    # Remove redundant spaces
    return " ".join(cleaned_text.split())


def log_failed_task(url, error_type, error_message):
    """Logs a failed task to CSV."""

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
