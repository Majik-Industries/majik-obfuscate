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


def test_size_off_by_one():
    for algorithm in [
        majik.obfuscate.Algorithm.AES128,
        majik.obfuscate.Algorithm.AES192,
        majik.obfuscate.Algorithm.AES256,
    ]:
        ob = majik.obfuscate.Obfuscate(algorithm)
        for size in [128, 127, 129]:
            binary = os.urandom(size)
            text = random_text(size)

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
    for algorithm in [
        majik.obfuscate.Algorithm.AES128,
        majik.obfuscate.Algorithm.AES192,
        majik.obfuscate.Algorithm.AES256,
    ]:
        ob = majik.obfuscate.Obfuscate(algorithm)
        for size in [128, 127, 129]:
            binary = os.urandom(size)
            text = random_text(size)

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
