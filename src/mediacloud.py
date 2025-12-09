"""Manager for the MediaCloud API for fetching our data sources"""

from typing import Any

import mediacloud.api

SOURCES_PER_PAGE = 100  # the number of sources retrieved per page


def get_collection(collection: int, api_key: str) -> list[Any]:
    """Gets a collection from mediacloud given a collection number and API key

    Args:
        collection: The integer representing the collection on MediaCloud
        api_key: Your API key for accessing the MediaCloud API

    Returns:
        A list of sources from that collection

    """
    mc_directory = mediacloud.api.DirectoryApi(api_key)
    sources = []
    offset = 0
    while True:
        response = mc_directory.source_list(
            collection_id=collection, limit=SOURCES_PER_PAGE, offset=offset
        )
        print(response)
        sources += response["results"]
        if response["next"] is None:
            break
        offset += len(response["results"])
    return sources
