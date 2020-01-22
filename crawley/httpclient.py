import logging
import urllib
from enum import Enum
from urllib.error import HTTPError, URLError
from http.client import IncompleteRead
import urllib.request


http_ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"  # noqa


class Skipped(Enum):
    """Reason for skipping the URL."""

    UNICODE = 1  #: Charset mismatch
    HTTP = 2  #: Failed to connect
    SSL = 3  #: SSL certificate error
    PACKET = 4  #: Server sent a malformed or incomplete packet
    URL = 5  #: Error in URL


def get_url(url):
    logger = logging.getLogger()

    logger.info(f"Making request to {url}.")
    urllib.request.urlcleanup()
    try:
        return urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": http_ua})
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
