#!/usr/bin/env python3
# Dump INI file
""" Dump INI

"""
import argparse
import configparser
import base64
import os
import sys
import textwrap
import traceback

# My name is
SLIM_SHADY = os.path.basename(sys.argv[0])


class Counter:
    def __init__(self, initial=0):
        self._initial = 0
        self._value = initial

    @property
    def first(self):
        retval = True
        if self._initial == self._value:
            retval = False
        self._value += 1
        return retval


def parse_args():
    """ Parse command line arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "inifile",
        help="INI File [section] to dump",
    )
    parser.add_argument(
        "section",
        help="INI File [section] to dump",
    )
    parser.add_argument(
        "option",
        nargs="?",
        default=None,
        help="INI File option = to dump",
    )
    opts = parser.parse_args()
    return opts


def main(opts):
    """ Default entry point """
    cp = configparser.ConfigParser()

    with open(opts.inifile, "r") as fobj:
        cp.read_file(fobj)

    if opts.section not in cp:
        sys.stderr.write(f"Section [{opts.section}] does not exist\n")
        sys.exit(2)
    if opts.option:
        if opts.option not in cp[opts.section]:
            sys.stderr.write(
                f"Section [{opts.section}] has no option '{opts.option}'\n"
            )
            sys.exit(2)
        print(cp[opts.section][opts.option])
    else:
        wrapper = textwrap.TextWrapper()
        for key, value in cp[opts.section].items():
            counter = Counter()
            sys.stdout.write(
                "%s = %s\n"
                % (
                    key,
                    textwrap.indent(value, "    ", lambda x: counter.first),
                )
            )


if __name__ == "__main__":

    _opts = parse_args()
    try:
        main(_opts)
    except Exception as err:  # pylint: disable=W0703
        sys.stderr.write("%s\n" % (textwrap.fill(str(err))))
        sys.exit(1)
