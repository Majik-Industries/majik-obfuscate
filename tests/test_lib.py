import io
import os
import struct

# 3rd party
import pytest

# Local
import common
import majik.obfuscate

def test_enums():
    # Since these are set in stone for the header file,
    # it's best to test them for the hard coded values.
    assert majik.obfuscate.Algorithm.AES128.value == 1
    assert majik.obfuscate.Algorithm.AES192.value == 2
    assert majik.obfuscate.Algorithm.AES256.value == 3

    assert majik.obfuscate.DataType.TXT.value == 1
    assert majik.obfuscate.DataType.BIN.value == 2

def test_normal_run():
    for algorithm in common.ALGORITHMS:
        ob = majik.obfuscate.Obfuscate(algorithm=algorithm)
        for size in common.TESTSIZES:
            binval = os.urandom(size)
            txtval = common.random_text(size)

            # Test binary with parse
            ob.value = binval
            ob.parse(ob.obfuscated)
            assert ob.value == binval

            # Test binary with property asisgnment
            ob.value = binval
            x = ob.obfuscated
            ob.obfuscated = x
            assert ob.value == binval

            # Test text with parse
            ob.value = txtval
            ob.parse(ob.obfuscated)
            assert ob.value == txtval

            # Test text with property asisgnment
            ob.value = txtval
            x = ob.obfuscated
            ob.obfuscated = x
            assert ob.value == txtval
