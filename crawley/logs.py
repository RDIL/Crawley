"""
Copyright (c) 2019-present Reece Dunham.
You should have received a copy of
the MIT license with this program/distribution.
"""

import logging
import sys


class Streamer:
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

    def flush(self):
        pass


def configure_logger():
    logger = logging.getLogger()
    console_output = logging.StreamHandler(sys.stdout)
    file_output = logging.FileHandler(
        filename="log.txt", encoding="utf-8", mode="w"
    )
    for e in [file_output, console_output]:
        e.setFormatter(
            logging.Formatter("%(asctime)s : %(levelname)s : %(message)s")
        )
        logger.addHandler(e)
    logger.setLevel(logging.DEBUG)
    stdout_logger = logging.getLogger("STDOUT")
    sys.stdout = Streamer(stdout_logger, logging.INFO)

    stderr_logger = logging.getLogger("STDERR")
    sys.stderr = Streamer(stderr_logger, logging.ERROR)
