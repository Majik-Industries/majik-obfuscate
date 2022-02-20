#
# Copyright 2022 Shawn Michael
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Common functions for the CLI programs"""

import argparse
import logging.handlers
import sys
import textwrap
import traceback


def cli_parser():
    """Build common parser for CLI programs

    Returns:
        argparse.ArgumentParser
    """
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

    return parser


def start(callback, parse_args):
    """This is basically the common "if __main__" code for all CLI programs"""

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
    _log = logging.getLogger()
    _log.setLevel(logging.ERROR)

    try:
        callback(_opts)
    except Exception as err:  # pylint: disable=W0703
        _output = textwrap.fill(str(err))
        sys.stderr.write(f"{_output}\n")
        if _opts.debug:
            traceback.print_exc()
        sys.exit(1)
