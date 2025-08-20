# app/services/common/utils.py

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


@retry(
    retry=retry_if_exception_type(httpx.HTTPError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
)
async def get_json(url: str, headers: dict | None = None, params: dict | None = None) -> dict:
    """
    Perform a GET request and return JSON.
    Includes retry logic with exponential backoff for transient network failures.

    Args:
        url: The URL to fetch.
        headers: Optional HTTP headers.
        params: Optional query parameters.

    Returns:
        dict: Parsed JSON response.
    """
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, headers=headers, params=params)
        r.raise_for_status()
        return r.json()


def chunk_list(data: list, size: int):
    """
    Yield successive chunks from a list.

    Args:
        data: The list to split.
        size: Max size of each chunk.

    Example:
        >>> list(chunk_list([1,2,3,4,5], 2))
        [[1,2],[3,4],[5]]
    """
    for i in range(0, len(data), size):
        yield data[i : i + size]
