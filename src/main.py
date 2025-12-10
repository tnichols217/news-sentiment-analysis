"""Main module for running data analysis on American News"""

from pathlib import Path

from src.article import get_all_articles

from .analyse import analyse_dir
from .envmanager import getenv
from .mediacloud import get_all_stories

if __name__ == "__main__":
    env = getenv()
    lib = Path("./data_lib")
    cen = Path("./data_cen")
    con = Path("./data_con")
    lib_art = Path("./articles_lib")
    cen_art = Path("./articles_cen")
    con_art = Path("./articles_con")
    get_all_stories(
        env["OPENMEDIACLOUD_SOURCE_NUM_LIBERAL"],
        env["OPENMEDIACLOUD_API_KEY"],
        lib,
    )
    get_all_stories(
        env["OPENMEDIACLOUD_SOURCE_NUM_CENTER"],
        env["OPENMEDIACLOUD_API_KEY"],
        cen,
    )
    get_all_stories(
        env["OPENMEDIACLOUD_SOURCE_NUM_CONSERVATIVE"],
        env["OPENMEDIACLOUD_API_KEY"],
        con,
    )
    get_all_articles(lib, lib_art)
    get_all_articles(cen, cen_art)
    get_all_articles(con, con_art)
    analyse_dir(lib_art, Path("output_lib.csv"))
    analyse_dir(cen_art, Path("output_cen.csv"))
    analyse_dir(con_art, Path("output_con.csv"))
