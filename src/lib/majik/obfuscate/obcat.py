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
=====
obcat
=====

This is an executable target used to print obfuscated data to stdout that comes
from a file generated with the ``majik.obfuscate`` library.

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
    parser.add_argument("file", help="Obfuscated file to grab the data from")
    opts = parser.parse_args()
    if opts.debug_log:
        opts.debug = True

    return opts


def main(opts):
    """Default entry point"""
    log = logging.getLogger(SLIM_SHADY)
    log.warning("Starting program")

    obfuscate = Obfuscate()
    with open(opts.file, "rb") as fobj:
        obfuscate.obfuscated = fobj.read()

    value = obfuscate.value
    if isinstance(value, str):
        sys.stdout.write(value)
    else:
        sys.stderr.buffer.write(value)


def start():
    """python console script entry point"""
    common_exe.start(main, parse_args)


if __name__ == "__main__":
    start()
