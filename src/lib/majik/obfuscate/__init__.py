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
================
Data Obfuscation
================

Obfuscate a payload so it's not obvious at a casual glance.

The obfuscate module will encrypt a payload and store the encryption key
as well as the payload withing the resulting output.  Even though the data
is technically encrypted, the encryption key sitting with the encrypted data
negates the actual encryption.  Thus the data is just obfuscated.

The reason for this design is that at some point fully automated systems need a
plain text password in order to get their job done. It's better to store that
password obfuscated instead of in plain text.  Security by obscurity.
Generally a bad habit but it does have limited use, this is one.

Obfuscated data format
======================

The payload format is.  The component size is in the parenthesis::

    +-------------+----------------+---------+------------+
    | header (12) | key (16,24,32) | iv (16) | data (16+) |
    +-------------+----------------+---------+------------+

Header
------

* **Version** 8 bit unsigned int
* **Data Type** 8 bit unsigned int
* **Algorithm** 8 bit unsigned int
* **Reserved** 8 bits
* **Size** 64 bit big endian unsigned int

Encryption Key (key)
--------------------

The key size depends on the Algorithm field of the header. This data size
will be either 16, 24 or 32 bytes depending on AES 128, 192 or 256 respectively
as the encryption algorithm chosen.

Initialization Vector (iv)
--------------------------

This is the AES Initialization Vector.  A random 16 byte blob.

Encrypted payload (data)
------------------------

This is the byte array of the obfuscated data.  This will be sized in multiples
of 16 bytes.


Module Contents
===============
"""

import collections
import enum
import io
import logging
import struct
import typing

# 3rd party
import Cryptodome.Cipher.AES
import Cryptodome.Random
import Cryptodome.Util.Padding

logging.getLogger(__name__).addHandler(logging.NullHandler())


CipherInfo = collections.namedtuple("CipherInfo", ["blocksz", "keysz"])

__version__ = "1.0.2"


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
    # pylint: disable=too-many-instance-attributes
    """Class used to create and read obfuscated data.

    The values remain encrypted within the class at all times (garbage
    collection not withstanding).  The value is decrypted each and every time
    it is accessed as the property :attr:`value`. This can be expensive
    if used frequently.

    Parameters:
        algorithm: Specify which encryption algorithm used to obfuscate the
            data.
    """

    def __init__(self, algorithm: Algorithm = Algorithm.AES128):
        if not isinstance(algorithm, Algorithm):
            raise ValueError("algorithm parameter must be of type Algorithm")

        self._alg_map = {
            Algorithm.AES128: CipherInfo(Cryptodome.Cipher.AES.block_size, 16),
            Algorithm.AES192: CipherInfo(Cryptodome.Cipher.AES.block_size, 24),
            Algorithm.AES256: CipherInfo(Cryptodome.Cipher.AES.block_size, 32),
        }
        self._version = 1
        self._algorithm = algorithm
        self._data_type = DataType.TXT
        self._data = io.BytesIO()
        self._info = self._alg_map[self._algorithm]
        self._iv = None
        self._key = None
        self._encrypted = None

        self._size = 0

    def _size_check(self):
        length = self._data.seek(0, io.SEEK_END)

        if length == 0:
            error = "You must set the value before you can use it"
        elif length < 60:
            # 60 is the minimum encrypted size for a 0 byte data packet
            error = "Invalid value to decrypt"
        else:
            error = None

        if error:
            raise ValueError(error)
        return length

    def parse(self, raw: bytes):
        """Parse an obfuscated byte blob.

        Load and parse the raw record. Using this function will overwrite
        any existing data stored in the class.  This function is called when
        you assign :attr:`obfuscated` a value.
        """
        self._data.seek(0)
        self._data.truncate()
        self._data.write(raw)
        length = len(raw)

        self._data.seek(0)
        # Parse the header block
        (
            self._version,
            data_type,
            algorithm,
            reserved,  # pylint: disable=unused-variable
            self._size,
        ) = struct.unpack(">BBBBQ", self._data.read(12))
        if self._version != 1:
            raise ValueError(f"Unknown version: {self._version}")

        self._data_type = DataType(data_type)
        self._algorithm = Algorithm(algorithm)

        self._info = self._alg_map.get(self._algorithm, None)
        if not self._info:
            raise ValueError(f"Unimplemented algorithm: {self._algorithm}")

        # With pkcs7 padding length will always be greater than the actual
        # payload size.
        if length < 12 + self._info.keysz + self._info.blocksz + self._size:
            raise ValueError("Corrupted data: invalid size")

        self._key = self._data.read(self._info.keysz)
        self._iv = self._data.read(self._info.blocksz)

        # Currently we are only dependent on AES... so it's hard coded here
        self._encrypted = self._data.read()

    @property
    def value(self) -> typing.Union[bytes, str]:
        """(bytes or str) Unobfuscated value.

        This is a read/write property.  Assinging a value to this property
        will create a new obfuscated payload automatically.  Reading this
        property will decrypt the value at time of use.
        """
        cipher = Cryptodome.Cipher.AES.new(
            self._key, Cryptodome.Cipher.AES.MODE_CBC, self._iv
        )
        payload = Cryptodome.Util.Padding.unpad(
            cipher.decrypt(self._encrypted), self._info.blocksz
        )
        if len(payload) != self._size:
            raise ValueError(
                f"Size mismatch: expected {self._size} got {len(payload)}"
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
        self._info = self._alg_map.get(self._algorithm, None)
        if not self._info:
            raise ValueError("Unimplemented algorithm: {self._algorithm}")

        self._key = Cryptodome.Random.get_random_bytes(self._info.keysz)
        self._iv = Cryptodome.Random.get_random_bytes(self._info.blocksz)

        cipher = Cryptodome.Cipher.AES.new(
            self._key, Cryptodome.Cipher.AES.MODE_CBC, self._iv
        )
        self._encrypted = cipher.encrypt(
            Cryptodome.Util.Padding.pad(data, self._info.blocksz)
        )

        self._data.truncate()
        self._data.seek(0)
        self._data.write(
            struct.pack(
                ">BBBBQ",
                1,  # Version
                self._data_type.value,
                self._algorithm.value,
                0,  # Reserved
                len(payload),
            )
        )
        self._data.write(self._key)
        self._data.write(self._iv)
        self._data.write(self._encrypted)

    @property
    def obfuscated(self) -> bytes:
        """(bytes) Obfuscated value

        This is a read/write property.  Assigning a value will attempt to
        parse the bytes as an obfuscated value.

        The value read can be written to a file.  It is portable between
        architectures.

        Raises:
            ValueError if the data can not be parsed
        """
        self._size_check()
        return self._data.getvalue()

    @obfuscated.setter
    def obfuscated(self, value: bytes):
        if not isinstance(value, bytes):
            raise ValueError("Obfuscate.obfuscated must be of type 'bytes'")
        self.parse(value)
