#!/usr/bin/env python3
""" Default program template

"""
import argparse
import base64
import logging
import logging.handlers
import os
import sys
import textwrap
import traceback

# local imports
from . import Obfuscate, Algorithm

# My name is
SLIM_SHADY = os.path.basename(sys.argv[0])


def parse_args():
    """ Parse command line arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug",
        dest="debug",
        default=False,
        action="store_true",
        help="Turn on debug output",
    )
    parser.add_argument(
        "--debug-log",
        dest="debug_log",
        default=None,
        help="Specify a file for debug output. Implies --debug",
    )
    parser.add_argument(
        "--verbose",
        dest="verbose",
        default=False,
        action="store_true",
        help="Turn on verbose output",
    )
    parser.add_argument(
        "--log",
        dest="output_log",
        default=None,
        help="Specify a log file to log debug data to",
    )
    parser.add_argument("file", help="File to write obfuscated data to.")
    parser.add_argument(
        "data",
        nargs="?",
        default=None,
        help="Data to write to <file>.  [Default: prompt]",
    )
    opts = parser.parse_args()
    if opts.debug_log:
        opts.debug = True

    return opts


def main(opts):
    """ Default entry point """
    log = logging.getLogger(SLIM_SHADY)
    log.warning("Starting program")

    if opts.data is None:
        payload = input("Data: ")
    else:
        payload = opts.data

    obfuscate = Obfuscate()
    obfuscate.value = payload

    with open(opts.file, "wb") as fobj:
        fobj.write(obfuscate.obfuscated)


def start():
    _opts = parse_args()
    # Set up stderr logging
    _stderr = logging.StreamHandler(stream=sys.stderr)

    if _opts.debug:
        if _opts.debug_log:
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s %(levelname)s %(name)s: %(message)s",
                filename=_opts.debug_log,
                filemode="a",
                handlers=[_stderr],
            )
        else:
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s %(levelname)s %(name)s: %(message)s",
                handlers=[_stderr],
            )
    elif _opts.verbose:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
            handlers=[_stderr],
        )
    else:
        logging.basicConfig(
            level=logging.ERROR,
            format="%(name)s: %(message)s",
            handlers=[_stderr],
        )
    _log = logging.getLogger(SLIM_SHADY)
    _log.setLevel(logging.ERROR)

    try:
        main(_opts)
    except Exception as err:  # pylint: disable=W0703
        sys.stderr.write("%s\n" % (textwrap.fill(str(err))))
        if _opts.debug:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    start()
