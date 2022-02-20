import io
import os
import struct

# 3rd party
import pytest

# Local
import majik.obfuscate


def random_text(size):
    output = []
    while True:
        block = os.urandom(size * 4)
        for val in block:
            if val >= 32 and val < 127:
                output.append(chr(val))
            if len(output) == size:
                break
        if len(output) == size:
            break

    return "".join(output)


def test_algorithm():
    # The acutal numerical mappings here are set in stone and cann not be
    # changed.  These map to actual integers in the file.

    aes128 = majik.obfuscate.Algorithm.AES128
    aes192 = majik.obfuscate.Algorithm.AES192
    aes256 = majik.obfuscate.Algorithm.AES256

    assert aes128.value == 1
    assert aes192.value == 2
    assert aes256.value == 3


