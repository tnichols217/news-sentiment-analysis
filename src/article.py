"""Module for downloading articles given links"""

import json
from pathlib import Path
from typing import cast

from newspaper.article import Article

from .mediacloud import ArticleType


def get_article(url: str) -> tuple[str, set[str]]:
    """Gets an article text given its URL

    Args:
        url: The URL to the article as a string

    Returns:
        The raw text of the article queried and the tags of that article

    """
    article = Article(url)
    try:
        _ = article.download()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

        article.parse()
        return str(article.text), cast(set[str], article.tags)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
    except:  # noqa: E722
        print(f"Failed to download article {url}")
        return "", set({})


def get_all_articles(input_dir: Path, output_dir: Path) -> None:
    """Gets all articles from article sources stored in a directory

    Args:
        input_dir: Input directory of json articles
        output_dir: Output directory for articles with text

    """
    files = input_dir.glob("*.json")
    output_dir.mkdir(exist_ok=True, parents=True)
    article_num = 0
    for fp in files:
        with fp.open("r") as f:
            content = cast(list[ArticleType], json.load(f))
            for item in content:
                new_path = output_dir / f"{article_num}.json"
                article_num += 1
                with new_path.open("w") as nf:
                    text, tags = get_article(item["url"])
                    item["text"] = text
                    item["tags"] = list(tags)
                    json.dump(item, nf, indent=4)


if __name__ == "__main__":
    a = get_all_articles(Path("data_lib"), Path("articles_lib"))
    a = get_all_articles(Path("data_cen"), Path("articles_cen"))
    a = get_all_articles(Path("data_con"), Path("articles_con"))
    print(a)
