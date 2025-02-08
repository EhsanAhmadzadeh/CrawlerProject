import httpx
import asyncio
import logging
from typing import Any, Dict, Optional, Union
from config import AppConfig

# We define one async client at module level
# so we don't create new clients repeatedly in each call.
# This helps keep connections alive (persistent HTTP).
_client = httpx.AsyncClient(timeout=AppConfig.REQUEST_TIMEOUT)


async def async_send_request(
    url: str,
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Union[str, int]]] = None,
    headers: Optional[Dict[str, str]] = None,
    retries: int = 3,
) -> Dict[str, Any]:
    """
    Sends an HTTP request using httpx with basic retry logic.

    :param url: The target URL.
    :param method: HTTP method ('GET' or 'POST').
    :param params: Query parameters (for GET).
    :param data: Form data (for POST).
    :param headers: Custom headers.
    :param retries: Number of retries on failure.
    :return: { 'status_code': int, 'text': str } or { 'error': str }
    """
    attempt = 0
    while attempt < retries:
        try:
            response = await _client.request(
                method=method,
                url=url,
                params=params,
                data=data,
                headers=headers,
            )
            # Raise an exception for 4xx/5xx status codes
            response.raise_for_status()
            return {"status_code": response.status_code, "text": response.text}
        except httpx.HTTPError as err:
            logging.warning(f"HTTP error on attempt {attempt+1}/{retries} for {url}: {err}")
            attempt += 1
            await asyncio.sleep(1)  # short delay before retry
        except Exception as e:
            logging.error(f"Request failed unexpectedly: {e}")
            return {"error": str(e)}

    return {"error": f"Request failed after {retries} attempts."}
