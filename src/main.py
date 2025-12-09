"""Main module for running data analysis on American News"""

import json
from pathlib import Path

from .envmanager import getenv
from .mediacloud import get_collection

if __name__ == "__main__":
    env = getenv()
    collection = get_collection(
        env["OPENMEDIACLOUD_SOURCE_NUM"], env["OPENMEDIACLOUD_API_KEY"]
    )
    fp = Path("./data.json")
    with Path.open(fp, "w") as f:
        json.dump(collection, f)
