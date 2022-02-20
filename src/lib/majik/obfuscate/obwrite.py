#!/usr/bin/env python3
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

"""
=======
obwrite
=======

Generate an obfuscated file using the ``majik.obufscate`` library.

"""

# pylint: disable=R0801
import logging
import os
import sys

# local imports
from . import Obfuscate
from . import common_exe

# My name is
SLIM_SHADY = os.path.basename(sys.argv[0])


def parse_args():
    """Parse command line arguments"""
    parser = common_exe.cli_parser()
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
    """Default entry point"""
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
    """python console script entry point"""
    common_exe.start(main, parse_args)


if __name__ == "__main__":
    start()
