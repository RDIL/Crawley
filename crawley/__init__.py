"""
Copyright (c) 2019-present Reece Dunham.
You should have received a copy of
the MIT license with this program/distribution.
"""

import gc
from bs4 import BeautifulSoup
from filehandlers import AbstractFile, FileManipulator
import logging
from typing import Optional
from .logs import configure_logger
from .httpclient import Skipped, get_url

ourfile = FileManipulator(AbstractFile("crawler-list.txt"))
logger = logging.getLogger()

to_check: list = ["http://dmoz-odp.org"]


def is_valid_url(a_url) -> bool:
    return (
        not a_url.startswith("/")
        and not a_url.startswith(".")
        and not a_url.startswith("#")
        and not a_url == ""
        and not a_url.startswith("?")
        and not a_url.endswith(".jpg")
        and not a_url.endswith(".png")
        and not a_url.endswith(".svg")
        and not a_url.endswith(".ico")
        and not a_url.endswith(".webp")
        and not a_url.startswith("javascript")
        and not a_url.endswith(".onion")
        and not a_url.startswith("	")  # tab character
        and not a_url.startswith(" ")  # space bar
        and not a_url.startswith("mailto:")
        and not a_url.startswith("tel:")
        and not a_url.endswith(".exe")
        and not a_url.endswith(".pdf")
        and "under18" not in a_url
        and "child" not in a_url
        and "minor" not in a_url
        and "kid" not in a_url
        and a_url not in ourfile.get_cache()
    )


def valid_response(down) -> bool:
    return not (
        down == Skipped.UNICODE
        or down == Skipped.SSL
        or down == Skipped.HTTP
        or down == Skipped.PACKET
        or down == Skipped.URL
    )


def startup() -> None:
    """Start the program."""
    gc.enable()
    configure_logger()
    logger.info("Clearing file...")
    open("crawler-list.txt", mode="w")
    logger.warning("Starting. This may become very resource intensive!!")
    manage_soup(
        BeautifulSoup(get_url(to_check[0]), "html.parser"), to_check[0]
    )
    functionality_loop()


def functionality_loop() -> None:
    while True:
        for a_url in to_check:
            if a_url is None:
                continue
            ourfile.refresh()
            if is_valid_url(a_url):
                down = get_url(a_url)
                if not valid_response(down=down):
                    logger.warning("Failed to fetch URL. Skipping...")
                    logger.debug(f"Skipping {a_url}.")
                    continue
                manage_soup(
                    soup=BeautifulSoup(down, "html.parser"), url=a_url
                )
                note_url(a_url)


def manage_soup(soup: BeautifulSoup, url: Optional[str]) -> None:
    assert type(soup) is BeautifulSoup
    for anchor in soup.find_all("a"):
        href = anchor.get("href")
        if href not in to_check and href is not None:
            to_check.append(href)

    del to_check[to_check.index(url)]
    for i, x in enumerate(to_check):
        if not is_valid_url(to_check[i]):
            del to_check[i]


def note_url(a_url) -> None:
    try:
        ourfile.write_to_file(a_url + "\n")
        ourfile.refresh()
    except UnicodeError as f:
        logger.error(f)


if __name__ == "__main__":
    startup()
