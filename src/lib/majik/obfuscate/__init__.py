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
Obfuscate a payload so it's not obvious at a casual glance.

The obfuscate module will encrypt a payload and store the encryption key
as well as the payload withing the resulting output.  Even though the data
is technically encrypted, the encryption key sitting with the encrypted data
negating the actual encryption.  Thus the data is just obfuscated.

The design behind this is that any automated system somewhere has a password
stored on disk.  It's slightly better to store that password obfuscated
instead of in plain text.  Security by obscurity.   Generally a bad habit
but it does have limited use, this is one.

The file format is:

32 bit integer big endian   <- Header
64 bit integer big endian   <- Payload size
Encryption key
Encryption IV
Encrypted data

"""

import collections
import enum
import io
import logging
import os
import struct
import typing

# 3rd party
import Cryptodome.Cipher.AES
import Cryptodome.Random
import Cryptodome.Util.Padding

logging.getLogger(__name__).addHandler(logging.NullHandler())


CipherInfo = collections.namedtuple("CipherInfo", ["blocksz", "keysz"])


@enum.unique
class DataType(enum.Enum):
    """Enum describing valid data types

    There are only 256 possible total values here.  The values of this enum
    must fit in one byte.
    """

    TXT = 1
    BIN = 2


@enum.unique
class Algorithm(enum.IntEnum):
    """Enum describing valid encryption schemes.

    There are only 256 possible total values here.  The values of this enum
    must fit in one byte.
    """

    AES128 = 1
    AES192 = 2
    AES256 = 3


class Obfuscate:
    """Class used to create and read obfuscated data.

    The values remain encrypted within the class at all times (garbage
    collection not withstanding).  The value is decrypted each and every time
    it is accessed as the property Obfuscate.value. This can be expensive
    if used frequently.

    Parameters:
        algorithm: Specify which encryption algorithm used to obfuscate the
            data.
    """

    INFO = {
        Algorithm.AES128: CipherInfo(Cryptodome.Cipher.AES.block_size, 16),
        Algorithm.AES192: CipherInfo(Cryptodome.Cipher.AES.block_size, 24),
        Algorithm.AES256: CipherInfo(Cryptodome.Cipher.AES.block_size, 32),
    }

    def __init__(self, algorithm: Algorithm = Algorithm.AES128):
        if not isinstance(algorithm, Algorithm):
            raise ValueError("algorithm parameter must be of type Algorithm")

        self._version = 1
        self._algorithm = algorithm
        self._data_type = DataType.TXT
        self._data = io.BytesIO()
        self._info = self.INFO[self._algorithm]
        self._iv = None
        self._key = None
        self._encrypted = None

        self._size = 0

    def _size_check(self):
        length = self._data.seek(0, io.SEEK_END)

        if length == 0:
            raise ValueError("You must set the value before you can use it")
        elif length < 60:
            # 60 is the minimum encrypted size for a 0 byte data packet
            raise ValueError("Invalid value to decrypt")
        return length

    def parse(self, raw: bytes):
        self._data.seek(0)
        self._data.truncate()
        self._data.write(raw)
        length = len(raw)

        self._data.seek(0)
        # Parse the header block
        header, self._size = struct.unpack(">IQ", self._data.read(12))
        self._version = (header >> 24) & 0xFF
        if self._version != 1:
            raise ValueError("Unknown version: %d" % self._version)

        self._data_type = DataType((header >> 16) & 0xFF)
        self._algorithm = Algorithm((header >> 8) & 0xFF)

        self._info = self.INFO.get(self._algorithm, None)
        if not self._info:
            raise ValueError("Unimplemented algorithm: %s" % self._algorithm)

        # With pkcs7 padding length will always be greater than the actual
        # payload size.
        if length <= 12 + self._info.keysz + self._info.blocksz + self._size:
            raise ValueError("Corrupted data: invalid size")

        self._key = self._data.read(self._info.keysz)
        self._iv = self._data.read(self._info.blocksz)

        # Currently we are only dependent on AES... so it's hard coded here
        self._encrypted = self._data.read()

    @property
    def value(self) -> typing.Union[bytes, str]:
        cipher = Cryptodome.Cipher.AES.new(
            self._key, Cryptodome.Cipher.AES.MODE_CBC, self._iv
        )
        payload = Cryptodome.Util.Padding.unpad(
            cipher.decrypt(self._encrypted), self._info.blocksz
        )
        if len(payload) != self._size:
            raise ValueError(
                "Size mismatch: expected %d got %d"
                % (self._size, len(payload))
            )
        if self._data_type == DataType.TXT:
            payload = payload.decode("utf-8")
        return payload

    @value.setter
    def value(self, payload: typing.Union[bytes, str]):
        if isinstance(payload, bytes):
            data = payload
            self._data_type = DataType.BIN
        elif isinstance(payload, str):
            data = payload.encode("utf-8")
            self._data_type = DataType.TXT
        else:
            raise ValueError("value must be of type 'bytes' or 'str'")

        self._size = len(payload)
        self._info = self.INFO.get(self._algorithm, None)
        if not self._info:
            raise ValueError("Unimplemented algorithm: %s" % self._algorithm)

        self._key = Cryptodome.Random.get_random_bytes(self._info.keysz)
        self._iv = Cryptodome.Random.get_random_bytes(self._info.blocksz)

        cipher = Cryptodome.Cipher.AES.new(
            self._key, Cryptodome.Cipher.AES.MODE_CBC, self._iv
        )
        self._encrypted = cipher.encrypt(
            Cryptodome.Util.Padding.pad(data, self._info.blocksz)
        )

        header = (
            (1 << 24)
            + (self._data_type.value << 16)  # Obfuscate Version
            + (self._algorithm.value << 8)  # Data type
            + 0  # Encryption Algorithm  # Reserved
        )

        self._data.truncate()
        self._data.seek(0)
        self._data.write(struct.pack(">IQ", header, len(payload)))
        self._data.write(self._key)
        self._data.write(self._iv)
        self._data.write(self._encrypted)

    @property
    def obfuscated(self) -> bytes:
        """Obfuscated value"""
        length = self._size_check()
        return self._data.getvalue()

    @obfuscated.setter
    def obfuscated(self, value: bytes):
        if not isinstance(value, bytes):
            raise ValueError("Obfuscate.obfuscated must be of type 'bytes'")
        self.parse(value)

if __name__ == "__main__":
    block = "0123456789" * 1000
    x = Obfuscate()
    x.value = ""
    print("Empty: [%s]" % x.value)
    print("Data size: %d" % len(x.obfuscated))
    for i in range(64):
        x.value = block[0:i]
        print(x.value)
        print("Data size: %d" % len(x.obfuscated))
