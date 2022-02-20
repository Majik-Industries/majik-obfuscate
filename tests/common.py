import os

# Local
import majik.obfuscate

ALGORITHMS = [
    majik.obfuscate.Algorithm.AES128,
    majik.obfuscate.Algorithm.AES192,
    majik.obfuscate.Algorithm.AES256,
]

TESTSIZES = [0, 1, 15, 16, 17, 16384, 1048575, 1048576, 1048577]


def random_text(size):
    output = []
    while True:
        block = os.urandom(size * 4)
        for val in block:
            if len(output) == size:
                break
            if val >= 32 and val < 127:
                output.append(chr(val))
        if len(output) == size:
            break

    return "".join(output)
