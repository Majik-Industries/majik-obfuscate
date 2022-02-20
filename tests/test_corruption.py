import io
import os
import struct

# 3rd party
import pytest

# Local
import common
import majik.obfuscate

# Strip 0
OBO_TEST_SIZES = [x for x in common.TESTSIZES if x > 0]

def test_size_off_by_one():
    for algorithm in common.ALGORITHMS:
        ob = majik.obfuscate.Obfuscate(algorithm)
        for size in OBO_TEST_SIZES:
            binary = os.urandom(size)
            text = common.random_text(size)

            # Test off by one either direction
            for offset in [1, -1]:
                for value in [text, binary]:
                    ob.value = value
                    assert ob.value == value

                    fobj = io.BytesIO()
                    fobj.write(ob.obfuscated)
                    fobj.seek(4)
                    size  = struct.unpack(">Q", fobj.read(8))[0]
                    size += offset
                    fobj.seek(4)
                    fobj.write(struct.pack(">Q", size))
                    ob.obfuscated = fobj.getvalue()
                    with pytest.raises(ValueError):
                        ob.value

def test_bad_version():
    for algorithm in common.ALGORITHMS:
        ob = majik.obfuscate.Obfuscate(algorithm)
        for size in common.TESTSIZES:
            binary = os.urandom(size)
            text = common.random_text(size)

            # Test off by one either direction
            for offset in [1, -1]:
                for value in [text, binary]:
                    ob.value = value
                    assert ob.value == value

                    fobj = io.BytesIO()
                    fobj.write(ob.obfuscated)
                    fobj.seek(0)
                    header  = struct.unpack(">i", fobj.read(4))[0]
                    version = header >> 24 & 0xff
                    version += offset
                    header = (header & 0xffffff) +  (version << 24)
                    fobj.seek(0)
                    fobj.write(struct.pack(">i", header))
                    with pytest.raises(ValueError):
                        ob.obfuscated = fobj.getvalue()
                        ob.value
