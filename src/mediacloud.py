"""Manager for the MediaCloud API for fetching our data sources"""

import datetime
import json
import time
from datetime import datetime as dt
from pathlib import Path
from typing import TypedDict, cast

import mediacloud.api

SOURCES_PER_PAGE = 1000  # the number of sources retrieved per page (max=1000)
WAIT_TIME = 31  # due to having a 2 req/min limit on the API


class ArticleType(TypedDict):
    """Class for the article type serialized"""

    id: str
    indexed_date: str
    language: str
    media_name: str
    media_url: str
    publish_date: str
    title: str
    url: str
    text: str
    tags: list[str]


class InputArticleType(TypedDict):
    """Class for the article type returned by MediaCloud"""

    id: str
    indexed_date: datetime.datetime | None
    language: str
    media_name: str
    media_url: str
    publish_date: datetime.datetime | None
    title: str
    url: str


class SourceType(TypedDict):
    """Class for the Source type returned by MediaCloud"""

    id: int
    name: str
    url_search_string: str
    label: str
    homepage: str
    notes: str
    platform: str
    stories_per_week: int
    first_story: str
    created_at: str
    modified_at: str
    pub_country: str
    pub_state: str
    primary_language: str
    media_type: str
    last_rescraped: str
    last_rescraped_msg: str
    collection_count: int
    alternative_domains: list[str]


def get_all_sources(collection: int, api_key: str) -> list[SourceType]:
    """Gets a collection from mediacloud given a collection number and API key

    Args:
        collection: The integer representing the collection on MediaCloud
        api_key: Your API key for accessing the MediaCloud API

    Returns:
        A list of sources from that collection

    """
    mc_directory = mediacloud.api.DirectoryApi(api_key)
    sources: list[SourceType] = []
    offset = 0
    while True:
        response = mc_directory.source_list(  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
            collection_id=collection, limit=SOURCES_PER_PAGE, offset=offset
        )
        print(response)  # pyright: ignore[reportUnknownArgumentType]
        res = cast(list[SourceType], response["results"])
        sources += res
        if response["next"] is None:
            break
        offset += len(res)
    return sources


def get_all_stories(collection: int, api_key: str, media_dir: Path) -> None:
    """Gets a collection from mediacloud given a collection number and API key

    Args:
        collection: The integer representing the collection on MediaCloud
        api_key: Your API key for accessing the MediaCloud API
        media_dir: Directory to save the fetched articles to

    """
    mc_search = mediacloud.api.SearchApi(api_key)
    media_dir.mkdir(parents=True, exist_ok=True)

    pagination_token: str | None = None
    more_stories = True
    page_num = 0
    while more_stories:
        page, pagination_token = cast(
            tuple[list[InputArticleType], str | None],
            mc_search.story_list(  # pyright: ignore[reportUnknownMemberType]
                "*",
                start_date=dt.fromtimestamp(0, datetime.UTC),
                end_date=dt.now(datetime.UTC),
                collection_ids=[collection],
                pagination_token=pagination_token,
            ),
        )
        pages: list[ArticleType] = [p | {  # pyright: ignore[reportAssignmentType]
                "publish_date": p["publish_date"].isoformat()
                if p["publish_date"]
                else "",
                "indexed_date": p["indexed_date"].isoformat()
                if p["indexed_date"]
                else "",
                "tags": [],
                "text": "",
            } for p in page]
        with Path.open(media_dir / f"{page_num}.json", "w") as f:
            json.dump(pages, f, indent=4)
        page_num += 1
        print(pages)
        more_stories = pagination_token is not None
        time.sleep(31)
