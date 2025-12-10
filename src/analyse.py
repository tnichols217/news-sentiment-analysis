"""Module for parallel sentiment processing"""

import csv
import json
from multiprocessing import Pool
from pathlib import Path
from typing import Any, cast

from transformers import PreTrainedTokenizer, TextClassificationPipeline

from .mediacloud import ArticleType

subjectivity: TextClassificationPipeline | None = None
sentiment: TextClassificationPipeline | None = None


def init_worker() -> None:
    """Loads the HuggingFace pipelines into global vars."""
    global subjectivity, sentiment  # noqa: PLW0603
    from transformers import pipeline  # noqa: PLC0415

    print("Initializing worker… loading models")

    subjectivity = pipeline(
        "text-classification",
        model="GroNLP/mdebertav3-subjectivity-multilingual",
        device="cuda:0",
    )

    sentiment = pipeline(
        "text-classification",
        model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
        device="cuda:1",
    )

    print("Models loaded")


def chunk_text(
    text: str, tokenizer: PreTrainedTokenizer, max_tokens: int = 200
) -> list[str]:
    """Chunks text to smaller pieces due to token limits

    Args:
        text: The text to be chunked
        tokenizer: The tokenizer to use to chunk by
        max_tokens: The number of tokens to chunk to

    Returns:
        Chunks of text at specified size

    """
    tokens = tokenizer.encode(text, add_special_tokens=False)  # pyright: ignore[reportUnknownMemberType]
    return [
        tokenizer.decode(tokens[i : i + max_tokens], skip_special_tokens=True).strip()  # pyright: ignore[reportUnknownMemberType]
        for i in range(0, len(tokens), max_tokens)
    ]


def get_sub_sen(text: str) -> tuple[float, float]:
    """Gets the Subjectivity and Sentiment from a piece of text

    Args:
        text: The text to be analysed

    Returns:
        A tuple of its subjectivity (opinion/fact) and sentiment (positive/negative)

    """
    import statistics  # noqa: PLC0415

    if subjectivity is None or sentiment is None:
        print("Worker not initialized!")
        return (0.0, 0.0)
    subj_list = subjectivity(chunk_text(text, subjectivity.tokenizer), batch_size=8)  # pyright: ignore[reportArgumentType]
    sent_list = sentiment(chunk_text(text, sentiment.tokenizer), batch_size=8)  # pyright: ignore[reportArgumentType]
    subj_mapped = [
        float((1 if subj["label"] == "LABEL_1" else -1) * subj["score"])  # pyright: ignore[reportAny]
        for subj in subj_list
    ]
    sent_mapped = [
        float(
            (1 if sent["label"] == "POSITIVE" else -1) * sent["score"]  # pyright: ignore[reportAny]
        )
        for sent in sent_list
    ]
    subj = statistics.median(subj_mapped)
    sent = statistics.median(sent_mapped)
    return (subj, sent)


def process_file(fp: Path) -> list[Any] | None:  # pyright: ignore[reportExplicitAny]
    """Executed in worker process. Returns one CSV row.

    Args:
        fp: The file to analyse

    Returns:
        The list of items to put into the CSV

    """
    try:
        with fp.open("r", encoding="utf-8") as f:
            article = cast(ArticleType, json.load(f))
    except:  # noqa: E722
        print(f"Failed to read file {fp!s}")
        return None

    if not article.get("text"):
        return None

    print(f"Processing: {article['title']}")

    sub, sen = get_sub_sen(article["text"])

    return [
        article["url"],
        article["media_name"],
        article["publish_date"],
        article["tags"],
        article["title"],
        sub,
        sen,
    ]


def analyse_dir(input_dir: Path, output_file: Path, workers: int = 2) -> None:
    """Analyses a directory of articles

    Args:
        input_dir: The input directory of articles
        output_file: A CSV containing information and sentiment for all articles
        workers: The number of threads to spawnn to parallelize this process

    """
    files = list(input_dir.glob("*.json"))

    with output_file.open("a", newline="", encoding="utf-8") as of:
        writer = csv.writer(of)

        with Pool(processes=workers, initializer=init_worker) as pool:
            for row in pool.imap_unordered(process_file, files):
                if row:
                    writer.writerow(row)
                    of.flush()


if __name__ == "__main__":
    analyse_dir(Path("articles_lib"), Path("output_lib.csv"))
    analyse_dir(Path("articles_cen"), Path("output_cen.csv"))
    analyse_dir(Path("articles_con"), Path("output_con.csv"))
