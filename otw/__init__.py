"""
Copyright (c) 2019-present Reece Dunham.
You should have received a copy of
the MIT license with this program/distribution.
"""

import os
import sys
import gc
from bs4 import BeautifulSoup
from filehandlers import *
from enum import Enum
from urllib.error import HTTPError, URLError
from http.client import IncompleteRead
import urllib.request
import logging
import json


class Skipped(Enum):
    UNICODE = 1
    HTTP = 2
    SSL = 3
    PACKET = 4
    URL = 5


entrypoint = os.getenv("MANUAL_EXCLUSIONS_FILE")
if entrypoint is not None:
    thejson = json.load(open(entrypoint, mode="r"))

ourfile = FileManipulator(AbstractFile("crawler-list.txt"))
logger = logging.getLogger()
http_ua = open("UserAgent", mode="r").readlines()[0].replace("\n", "")

theobject: dict = [
    {
        "political": {},
        "comedy": {},
        "informational": {},
        "tech": {},
        "culture": {},
        "history": {},
        "health": {},
        "science": {},
        "religion": {}
    }
]


def configure_logger():
    console_output = logging.StreamHandler(sys.stdout)
    file_output = logging.FileHandler(filename='log.txt', encoding='utf-8', mode='w')
    for e in [file_output, console_output]:
        e.setFormatter(logging.Formatter('%(asctime)s : %(levelname)s : %(message)s'))
        logger.addHandler(e)
    logger.setLevel(logging.DEBUG)
    stdout_logger = logging.getLogger('STDOUT')
    sys.stdout = Streamer(stdout_logger, logging.INFO)

    stderr_logger = logging.getLogger('STDERR')
    sys.stderr = Streamer(stderr_logger, logging.ERROR)


to_check: list = [
    "http://dmoz-odp.org"
]


class Streamer(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    :author: Ferry Boender <https://www.electricmonk.nl/log/>
    :license: GPL (https://www.electricmonk.nl/log/posting-license/)
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())


def is_valid_url(a_url) -> bool:
    defaults: bool = (
        not a_url.startswith("/")
        and not a_url.startswith(".")
        and not a_url.startswith("#")
        and not a_url == ''
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
    if entrypoint is not None:
        for text in thejson["no_scan"]:
            if text in a_url:
                return False
    return defaults


def valid_response(down) -> bool:
    return not (
            down == Skipped.UNICODE or
            down == Skipped.SSL or
            down == Skipped.HTTP or
            down == Skipped.PACKET or
            down == Skipped.URL
    )


def startup() -> None:
    """Start the program."""
    gc.enable()
    configure_logger()
    logger.info("Clearing file...")
    open("crawler-list.txt", mode="w")
    logger.warning("Starting. This may become very resource intensive!!")
    manage_soup(BeautifulSoup(get_url(to_check[0]), 'html.parser'), to_check[0])
    moved()


def moved() -> None:
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
                manage_soup(soup=BeautifulSoup(down, 'html.parser'), url=a_url)
                note_url(a_url)


def manage_soup(soup: BeautifulSoup, url: str) -> None:
    assert type(soup) is BeautifulSoup
    for anchor in soup.find_all('a'):
        href = anchor.get('href')
        if href not in to_check and href is not None:
            to_check.append(href)
    to_check.pop(to_check.index(url))
    for i, x in enumerate(to_check):
        if not is_valid_url(to_check[i]):
            to_check.pop(i)


def note_url(a_url) -> None:
    try:
        ourfile.get_file().wrap().write(f'{a_url}\n')
        ourfile.refresh()
    except UnicodeError as f:
        logger.error(f)


def get_url(url):
    logger.info(f"Making request to {url}.")
    urllib.request.urlcleanup()
    try:
        return urllib.request.urlopen(
            urllib.request.Request(
                url,
                headers={
                    'User-Agent': http_ua
                }
            )
        ).read()
    except HTTPError:
        return Skipped.HTTP
    except URLError:
        return Skipped.SSL
    except UnicodeError:
        return Skipped.UNICODE
    except IncompleteRead:
        return Skipped.PACKET
    except ConnectionResetError:
        return Skipped.HTTP
    except ConnectionAbortedError:
        return Skipped.PACKET
    except ValueError:
        return Skipped.URL


if __name__ == '__main__':
    startup()
