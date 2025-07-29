# BSD 3-Clause License
#
# Copyright (c) 2022-Present, nxtlo
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Basic implementation of a cheap container for dealing with byte buffers."""

from __future__ import annotations

__all__ = ("Bytes", "BytesMut", "Rawish", "Buffer")

import array
import ctypes as _ctypes
import io as _io
import struct
import sys as _sys
import typing
from collections import abc as collections

from sain import convert
from sain import iter as _iter
from sain import option as _option
from sain import result as _result
from sain.macros import assert_precondition
from sain.macros import deprecated
from sain.macros import rustc_diagnostic_item
from sain.macros import safe
from sain.macros import unsafe

from . import slice as _slice
from . import vec as _vec

if typing.TYPE_CHECKING:
    import inspect

    from typing_extensions import Self

    from sain import Option
    from sain import Result

    Chars = _iter.Iterator[_ctypes.c_char]
    """An iterator that maps each byte in `Bytes` as a character.

    It yields `ctypes.c_char` objects.

    This is created by calling `Bytes.chars()`
    """


Rawish: typing.TypeAlias = _io.StringIO | _io.BytesIO | _io.BufferedReader
"""A type hint for some raw data type.

This can be any of:
* `io.StringIO`
* `io.BytesIO`
* `io.BufferedReader`
* `memoryview`
"""

Buffer: typing.TypeAlias = bytes | bytearray | collections.Iterable[int]
"""A type hint for some bytes data type.

This can be any of:
* `bytes`
* `Bytes`
* `bytearray`
* `Iterable[int]`
* `memoryview[int]`
"""

ENCODING = "utf-8"


def unwrap_bytes(data: Rawish) -> bytes:
    if isinstance(data, _io.StringIO):
        buf = bytes(data.read(), encoding=ENCODING)
    else:
        # BufferedReader | BytesIO
        buf = data.read()
    return buf


@rustc_diagnostic_item("&[u8]")
@typing.final
class Bytes(convert.ToString, collections.Sequence[int], _slice.SpecContains[int]):
    """Provides immutable abstractions for working with bytes.

    It is an efficient container for storing and operating with bytes.
    It behaves very much like `array.array[int]` as well has the same layout.

    A `Bytes` objects are usually used within networking applications, but can also be used
    elsewhere as well.

    ## Construction
    `Bytes` object accept multiple rawish data types, See `Rawish` for all supported types.

    * `Bytes()`: Initialize an empty `Bytes` object
    * `from_str`: Create `Bytes` from `str`
    * `from_bytes`: Create `Bytes` from a `Buffer` bytes-like type
    * `from_raw`: Create `Bytes` from a `Rawish` type
    * `from_ptr`: Create `Bytes` that points to an `array.array[int]` without copying it
    * `Bytes.zeroed(count)`: Create `Bytes` filled with `zeroes * count`.

    Example
    -------
    ```py
    from sain import Bytes

    buf = Bytes.from_str("Hello")
    print(buf) # [72, 101, 108, 108, 111]
    # buf is currently immutable, to make it mutable use `buf.to_mut()`
    # the conversion costs nothing, as it just points to the same underlying array.
    buf_mut = buf.to_mut()
    buf_mut.put(32)
    assert buf_mut == b"Hello "
    ```
    """

    __slots__ = ("_buf",)

    def __init__(self) -> None:
        """Creates a new empty `Bytes`.

        This won't allocate the array and the returned `Bytes` will be empty.
        """
        self._buf: array.array[int] | None = None

    # construction

    @classmethod
    def from_str(cls, s: str) -> Bytes:
        """Create a new `Bytes` from a utf-8 string.

        Example
        -------
        ```py
        buffer = Bytes.from_str("💀")
        ```
        """
        b = cls()
        b._buf = array.array("B", s.encode(ENCODING))
        return b

    @classmethod
    def from_ptr(cls, arr: array.array[int]) -> Self:
        """Create a new `Bytes` from an array.

        The returned `Bytes` will directly point to `arr` without copying.

        Example
        -------
        ```py
        arr = array.array("B", b"Hello")
        buffer = Bytes.from_ptr(arr)
        ```
        """
        # this is technically an `assert` line
        # but Python isn't smart enough to inline and opt-out
        # this out of the generated bytecode.
        # so we'll just leave this under `if` statement.
        if __debug__:
            assert_precondition(
                arr.typecode == "B",
                f"array type must be `B`, not `{arr.typecode}`",
                TypeError,
            )

        b = cls()
        b._buf = arr
        return b

    @classmethod
    @unsafe
    def from_ptr_unchecked(cls, arr: array.array[int]) -> Self:
        """Create a new `Bytes` from an array, without checking the type code.

        The returned `Bytes` will directly point to `arr` without copying.

        ## Safety

        The caller must ensure that `arr` is of type `array.array[int]` with type code `B`.

        Example
        -------
        ```py
        arr = array.array("B", b"Hello")
        buffer = Bytes.from_ptr_unchecked(arr)
        ```
        """
        b = cls()
        b._buf = arr
        return b

    @classmethod
    def from_bytes(cls, buf: Buffer) -> Self:
        """Create a new `Bytes` from an initial bytes.

        Example
        -------
        ```py
        buffer = Bytes.from_bytes(b"SIGNATURE")
        ```
        """
        b = cls()
        b._buf = array.array("B", buf)
        return b

    @classmethod
    def from_raw(cls, raw: Rawish) -> Self:
        """Initialize a new `Bytes` from a `Rawish` data type.

        Example
        -------
        ```py
        with open('file.txt', 'rb') as file:
            buff = Bytes.from_raw(file)

        # in memory bytes io
        bytes_io = io.BytesIO(b"data")
        buffer1 = Bytes.from_raw(bytes_io)
        # in memory string io
        string_io = io.StringIO("data")
        buffer2 = Bytes.from_raw(string_io)
        ```
        """
        c = cls()
        c._buf = array.array("B", unwrap_bytes(raw))
        return c

    @classmethod
    def zeroed(cls, count: int) -> Self:
        """Initialize a new `Bytes` filled with `0 * count`.

        Example
        -------
        ```py
        ALLOC_SIZE = 1024 * 2
        buffer = Bytes.zeros(ALLOC_SIZE)
        assert buffer.len() == ALLOC_SIZE
        ```
        """
        c = cls()
        c._buf = array.array("B", [0] * count)
        return c

    # buffer evolution

    # These are getting deprecated because they're trivial.
    # maybe we impl a `String` type and include them later.
    # anyways, they won't be leaving for sometime until 2.0.0.

    @deprecated(
        since="1.3.0",
        removed_in="2.0.0",
        use_instead='Bytes.to_bytes().decode("utf8")',
        hint="Converting a bytes object to string is fairly trivial.",
    )
    def to_string(self) -> str:
        """Convert the bytes to a string.

        Same as `Bytes.to_str`
        """
        return self.to_str()

    @deprecated(
        since="1.3.0",
        removed_in="2.0.0",
        use_instead='Bytes.to_bytes().decode("utf8")',
        hint="Converting a bytes object to string is fairly trivial.",
    )
    def try_to_str(self) -> Result[str, bytes]:
        """A safe method to convert `self` into a string.

        This may fail if the `self` contains invalid bytes. strings
        needs to be valid utf-8.

        Example
        -------
        ```py
        buf = Bytes()
        sparkles_heart = [240, 159, 146, 150]
        buf.put_bytes(sparkles_heart)

        assert buf.try_to_str().unwrap() == "💖"
        ```

        Incorrect bytes
        ---------------
        ```py
        invalid_bytes = Bytes.from_bytes([0, 159, 146, 150])
        invalid_bytes.try_to_str().is_err()
        ```

        Returns
        -------
        `Result[str, bytes]`
            If successful, returns the decoded string, otherwise the original bytes that failed
            to get decoded.
        """
        try:
            return _result.Ok(self.to_bytes().decode(ENCODING))
        except UnicodeDecodeError as e:
            return _result.Err(e.object)

    @deprecated(
        since="1.3.0",
        removed_in="2.0.0",
        use_instead='str(Bytes, encoding="utf-8")',
        hint="Converting a bytes object to string is fairly trivial.",
    )
    def to_str(self) -> str:
        r"""Convert `self` to a utf-8 string.

        During the conversion process, any invalid bytes will get converted to
        [REPLACEMENT_CHARACTER](https://en.wikipedia.org/wiki/Specials_(Unicode_block))
        which looks like this `�`, so be careful on what you're trying to convert.

        Use `.try_to_str` try attempt the conversion in case of failure.

        Example
        -------
        ```py
        buf = Bytes()
        sparkles_heart = [240, 159, 146, 150]
        buf.put_bytes(sparkles_heart)

        assert buf.to_str() == "💖"
        ```

        Incorrect bytes
        ---------------
        ```py
        invalid_bytes = Bytes.from_bytes(b"Hello \xf0\x90\x80World")
        assert invalid_bytes.to_str() == "Hello �World"
        ```
        """
        if not self._buf:
            return ""

        return self._buf.tobytes().decode(ENCODING, errors="replace")

    def to_bytes(self) -> bytes:
        """Convert `self` into `bytes`, copying the underlying array into a new buffer.

        Example
        -------
        ```py
        buf = Bytes.from_str("Hello")
        assert buf.to_bytes() == b'Hello'
        ```
        """
        if not self._buf:
            return b""

        return self._buf.tobytes()

    def to_vec(self) -> _vec.Vec[int]:
        """Copies `self` into a new `Vec`.

        Example
        -------
        ```py
        buffer = Bytes.from_str([1, 2, 3, 4])
        # buffer and x can be modified independently.
        x = buffer.to_vec()
        """
        return _vec.Vec(self.copy())

    def leak(self) -> array.array[int]:
        """Consumes and leaks the `Bytes`, returning the contents as an `array[int]`,

        A new empty array is returned if the underlying buffer is not initialized.

        `self` will deallocate the underlying array, therefore it becomes unusable.

        Safety
        ------
        It is unsafe to access the leaked array from `self` after calling this function.

        Example
        -------
        ```py
        bytes = Bytes.from_str("chunks of data")
        consumed = bytes.leak()
        # `bytes` doesn't point to anything, this is undefined behavior.
        bytes.put(0)
        # access the array directly instead.
        consumed.tobytes() == b"chunks of data"
        ```
        """
        if self._buf is None:
            return array.array("B")

        arr = self._buf
        # We don't need to reference this anymore since the caller will own the array.
        del self._buf
        return arr

    def as_ptr(self) -> memoryview[int]:
        """Returns a read-only pointer to the buffer data.

        `pointer` here refers to a `memoryview` object.

        A `BufferError` is raised if the underlying sequence is not initialized.

        Example
        -------
        ```py
        buffer = Bytes.from_bytes(b"data")
        ptr = buffer.as_ptr()
        ptr[0] = 1 # TypeError: cannot modify read-only memory
        ```
        """
        return self.__buffer__(256).toreadonly()

    def as_ref(self) -> _slice.Slice[int]:
        """Get an immutable reference to the underlying sequence, without copying.

        An empty slice is returned if the underlying sequence is not initialized.

        Example
        -------
        ```py
        async def send_multipart(buf: Sequence[int]) -> None:
            ...

        buffer = Bytes.from_bytes([0, 0, 0, 0])
        await send_multipart(buffer.as_ref()) # no copy.
        ```
        """
        if self._buf is not None:
            return _slice.Slice(self)

        return _slice.Slice(())

    @safe
    def to_mut(self) -> BytesMut:
        """Convert `self` into `BytesMut`.

        This consumes `self` and returns a new `BytesMut` that points to the same underlying array,
        The conversion costs nothing.

        Notes
        -----
        * If `self` is not initialized, a new empty `BytesMut` is returned.
        * `self` will no longer be usable, as it will not point to the underlying array.

        The inverse method for this is `BytesMut.freeze()`

        Example
        -------
        ```py
        def modify(buffer: Bytes) -> BytesMut:
            buf = buffer.to_mut() # doesn't cost anything.
            buf.swap(0, 1)
            return buf

        buffer = Bytes.from_bytes([1, 2, 3, 4])
        new = modify(buffer)
        assert new == [2, 1, 3, 4]
        ```
        """
        # SAFETY: `Bytes.leak` returns an empty array
        # if `self` is uninitialized.
        return BytesMut.from_ptr_unchecked(self.leak())

    def raw_parts(
        self,
    ) -> tuple[int, int]:
        """Return `self` as tuple containing the memory address to the buffer and how many bytes it currently contains.

        An alias to `array.buffer_into`
        """
        if not self._buf:
            return (0x0, 0)

        return self._buf.buffer_info()

    def len(self) -> int:
        """Return the number of bytes in this buffer.

        Example
        -------
        ```py
        buf = Bytes.from_bytes([240, 159, 146, 150])
        assert buf.len() == 4
        ```
        """
        return self.__len__()

    def size(self) -> int:
        """The length in bytes of one array item in the internal representation.


        An alias to `array.itemsize`

        Example
        -------
        ```py
        buf = Bytes.from_bytes([240, 159, 146, 150])
        assert buf.size() == 1
        ```
        """
        if not self._buf:
            return 0
        return self._buf.itemsize

    def iter(self) -> _iter.TrustedIter[int]:
        """Returns an iterator over the contained bytes.

        This iterator yields all `int`s from start to end.

        Example
        -------
        ```py
        buf = Bytes.from_bytes((1, 2, 3))
        iterator = buf.iter()

        # map each byte to a character
        for element in iterator.map(chr):
            print(element)
        # ☺
        # ☻
        # ♥
        ```
        """
        return _iter.TrustedIter(self.as_ptr())

    def chars(self) -> Chars:
        """Returns an iterator over the characters of `Bytes`.

        This iterator yields all `int`s from start to end mapped as a `ctypes.c_char`.

        Example
        -------
        ```py
        b = Bytes.from_str("Hello")
        for char in b.chars():
            print(char)

        # c_char(b'H')
        # c_char(b'e')
        # c_char(b'l')
        # c_char(b'l')
        # c_char(b'o')
        ```
        """
        # The built-in map is actually faster than our own pure python adapter impl.
        return _iter.Iter(map(_ctypes.c_char, self))

    def is_empty(self) -> bool:
        """Check whether `self` contains any bytes or not.

        Example
        -------
        ```py
        buffer = Bytes()
        assert buffer.is_empty()
        ```
        """
        return not self._buf

    def split_off(self, at: int) -> Bytes:
        """Split the bytes off at the specified position, returning a new
        `Bytes` at the range of `[at : len]`, leaving `self` at `[at : bytes_len]`.

        if this bytes is empty, `self` is returned unchanged.

        Example
        -------
        ```py
        origin = Bytes.from_bytes((1, 2, 3, 4))
        split = origin.split_off(2)

        print(origin, split)  # [1, 2], [3, 4]
        ```

        Raises
        ------
        `RuntimeError`
            This method will raise if `at` > `len(self)`
        """
        len_ = self.len()
        if at > len_:
            raise RuntimeError(
                f"Index `at` ({at}) should be <= than len of `self` ({len_}) "
            ) from None

        # Either the list is empty or uninit.
        if not self._buf:
            return self

        split = self[at:len_]  # split the items into a new buffer.
        del self._buf[at:len_]  # remove the items from the original list.
        return split

    def split_first(self) -> Option[tuple[int, Bytes]]:
        """Split the first and rest elements of the bytes, If empty, `None` is returned.

        Example
        -------
        ```py
        buf = Bytes.from_bytes([1, 2, 3])
        split = buf.split_first()
        assert split == Some((1, [2, 3]))
        ```
        """
        if not self._buf:
            return _option.NOTHING

        # optimized to only one element in the buffer.
        if self.len() == 1:
            return _option.Some((self[0], Bytes()))

        first, rest = self[0], self[1:]
        return _option.Some((first, rest))

    def split_last(self) -> Option[tuple[int, Bytes]]:
        """Returns the last and rest of the elements of the bytes, If `self` is empty, `None` is returned.

        Example
        -------
        ```py
        buf = Bytes.from_bytes([0, 1, 2])
        last, elements = buf.split_last().unwrap()
        assert (last, elements) == (3, [1, 2])
        ```
        """
        if not self._buf:
            return _option.NOTHING

        len_ = self.len()
        # optimized to only one element in the buffer.
        if len_ == 1:
            return _option.Some((self[0], Bytes()))

        last, rest = self[-1], self[:-1]
        return _option.Some((last, rest))

    def split_at(self, mid: int) -> tuple[Bytes, Bytes]:
        """Divide `self` into two at an index.

        The first will contain all bytes from `[0:mid]` excluding `mid` it self.
        and the second will contain the remaining bytes.

        if `mid` > `self.len()`, Then all bytes will be moved to the left,
        returning an empty bytes in right.

        Example
        -------
        ```py
        buffer = Bytes.from_bytes((1, 2, 3, 4))
        left, right = buffer.split_at(0)
        assert left == [] and right == [1, 2, 3, 4]

        left, right = buffer.split_at(2)
        assert left == [1, 2] and right == [2, 3]
        ```

        The is roughly the implementation
        ```py
        self[0:mid], self[mid:]
        ```
        """
        return self[0:mid], self[mid:]

    # layout methods.

    @safe
    def copy(self) -> Bytes:
        """Create a copy of the bytes.

        Example
        -------
        ```py
        original = Bytes.from_bytes([255, 255, 255, 0])
        copy = original.copy()
        ```
        """
        if not self._buf:
            return Bytes()

        # SAFETY: `self._buf` is initialized.
        return self.from_ptr_unchecked(self._buf[:])

    def index(self, v: int, start: int = 0, stop: int = _sys.maxsize) -> int:
        """Return the smallest `i` such that `i` is the index of the first occurrence of `v` in the buffer.

        The optional arguments start and stop can be specified to search for x within a
        subsection of the array. Raise ValueError if x is not found
        """
        if not self._buf:
            raise ValueError from None

        return self._buf.index(v, start, stop)

    def count(self, x: int) -> int:
        """Return the number of occurrences of `x` in the buffer.

        Example
        --------
        ```py
        buf = Bytes([32, 32, 31])
        assert buf.count(32) == 2
        ```
        """
        if self._buf is None:
            return 0

        return self._buf.count(x)

    # special methods

    def __iter__(self) -> collections.Iterator[int]:
        if self._buf:
            return self._buf.__iter__()

        return ().__iter__()

    def __len__(self) -> int:
        return len(self._buf) if self._buf else 0

    def __repr__(self) -> str:
        if not self._buf:
            return "[]"

        return "[" + ", ".join(str(x) for x in self._buf) + "]"

    __str__ = __repr__

    def __bytes__(self) -> bytes:
        return self.to_bytes()

    def __buffer__(self, flag: int | inspect.BufferFlags) -> memoryview[int]:
        if not self._buf:
            raise BufferError("Cannot work with uninitialized bytes.")

        if _sys.version_info >= (3, 12):
            mem = self._buf.__buffer__(flag)
        else:
            # arrays in 3.11 and under don't implement the buffer protocol.
            mem = memoryview(self._buf)

        return mem

    def __contains__(self, byte: int) -> bool:
        return byte in self._buf if self._buf else False

    def __eq__(self, other: object, /) -> bool:
        if not self._buf:
            return False

        if isinstance(other, bytes):
            return self._buf.tobytes() == other

        # bytes IS a `Sequence[int]`, but not all `Sequence[int]`
        # represented as bytes.
        elif isinstance(other, collections.Sequence):
            return self._buf.tolist() == other

        return self._buf.__eq__(other)

    def __ne__(self, other: object, /) -> bool:
        return not self.__eq__(other)

    def __le__(self, other: object) -> bool:
        if not self._buf:
            return False

        if not isinstance(other, Bytes):
            return NotImplemented

        if not other._buf:
            return False

        return self._buf <= other._buf

    def __ge__(self, other: object) -> bool:
        if not self._buf:
            return False

        if not isinstance(other, Bytes):
            return NotImplemented

        if not other._buf:
            return False

        return self._buf >= other._buf

    def __lt__(self, other: object) -> bool:
        if not self._buf:
            return False

        if not isinstance(other, Bytes):
            return NotImplemented

        if not other._buf:
            return False

        return self._buf < other._buf

    def __gt__(self, other: object) -> bool:
        if not self._buf:
            return False

        if not isinstance(other, Bytes):
            return NotImplemented

        if not other._buf:
            return False

        return self._buf > other._buf

    @typing.overload
    def __getitem__(self, index: slice) -> Bytes: ...

    @typing.overload
    def __getitem__(self, index: int) -> int: ...

    @safe
    def __getitem__(self, index: int | slice) -> int | Bytes:
        if not self._buf:
            raise IndexError("Index out of range")

        if isinstance(index, slice):
            # SAFETY: `self._buf` is initialized.
            return self.from_ptr_unchecked(self._buf[index])

        return self._buf[index]

    def __reversed__(self) -> collections.Iterator[int]:
        return reversed(self._buf or ())

    # defined like `array`'s
    __hash__: typing.ClassVar[None] = None

    @safe
    def __copy__(self) -> Bytes:
        if not self._buf:
            return Bytes()

        return Bytes.from_ptr_unchecked(self._buf.__copy__())

    @safe
    def __deepcopy__(self, unused: typing.Any, /) -> Bytes:
        if not self._buf:
            return Bytes()

        return Bytes.from_ptr_unchecked(self._buf.__deepcopy__(unused))


@rustc_diagnostic_item("&mut [u8]")
@typing.final
class BytesMut(
    Bytes,  # pyright: ignore - we want to inherit from `Bytes`.
    collections.MutableSequence[int],
):
    """Provides mutable abstractions for working with bytes.

    It is an efficient container for storing and operating with bytes,
    It is built on-top of `array.array[int]`, which means you get all of `array[int]`'s operations.

    A `bytes` object is usually used within networking applications, but can also be used
    elsewhere as well.

    ## Construction
    You can create a `BytesMut` object in multiple ways.

    * `BytesMut()`: Initialize an empty `BytesMut` object
    * `from_str`: Create `BytesMut` from `str`
    * `from_bytes`: Create `BytesMut` from a `Buffer` bytes-like type
    * `from_raw`: Create `BytesMut` from a `Rawish` type
    * `from_ptr`: Create `BytesMut` that points to an `array.array[int]` without copying it
    * `BytesMut.zeroed(count)`: Create `BytesMut` filled with `zeroes * count`.

    Example
    -------
    ```py
    from sain import BytesNut

    buf = BytesMut()
    buffer.put_bytes(b"Hello")
    print(buffer) # [72, 101, 108, 108, 111]

    buf.put(32) # space
    assert buffer.to_bytes() == b"Hello "
    ```
    """

    __slots__ = ("_buf",)

    def __init__(self) -> None:
        """Creates a new empty `BytesMut`.

        This won't allocate the array and the returned `BytesMut` will be empty.
        """
        super().__init__()

    # default methods.

    def extend(self, src: Buffer) -> None:
        """Extend `self` from a `src`.

        Example
        -------
        ```py
        buf = Bytes()
        buf.extend([1, 2, 3])
        assert buf == [1, 2, 3]
        ```

        Parameters
        ----------
        src : `Buffer`
            Can be one of `Bytes`, `bytes`, `bytearray` or `Sequence[int]`

        Raises
        ------
        `OverflowError`
            If `src` not in range of `0..255`
        """
        if self._buf is None:
            # If it was `None`, we initialize it with a source instead of extending.
            self._buf = array.array("B", src)
        else:
            self._buf.extend(src)

    def put(self, src: int) -> None:
        """Append a byte at the end of the array.

        unlike `.put_bytes`, this method appends instead of extending the array
        which is faster if you're putting a single byte in a single call.

        Example
        -------
        ```py
        buf = Bytes()
        buf.put(32) # append a space to the end of the buffer
        assert buf.to_bytes() == b' '
        ```

        Parameters
        ----------
        src : `int`
            An unsigned integer, also known as `u8` to put.

        Raises
        ------
        `OverflowError`
            If `src` not in range of `0..255`
        """
        if self._buf is None:
            # If it was `None`, we initialize it with a source instead of appending.
            self._buf = array.array("B", [src])
        else:
            self._buf.append(src)

    def put_float(self, src: float) -> None:
        r"""Writes a single-precision (4 bytes) floating point number to `self` in big-endian byte order.

        The valid range for the float value is `-3.402823466e38` to `3.402823466e38`.

        Example
        -------
        ```py
        buf = BytesMut()
        buf.put_float(1.2)
        assert buf.to_bytes() == b'\x3f\x99\x99\x9a'
        ```

        Raises
        ------
        `OverflowError`
            If `src` is out of range.
        """
        assert_precondition(
            -3.402823466e38 <= src <= 3.402823466e38,
            f"Float {src} is out of range for a single-precision float",
            OverflowError,
        )
        bits = struct.pack(">f", src)

        if self._buf is None:
            self._buf = array.array("B", bits)
        else:
            self._buf.extend(bits)

    def put_char(self, char: str) -> None:
        """Append a single character to the buffer.

        This is the same as `self.put(ord(char))`.

        Example
        -------
        ```py
        buf = BytesMut()
        buf.put_char('a')
        assert buf == b"a"
        ```

        Parameters
        ----------
        char : `str`
            The character to put.
        """
        assert (ln := len(char)) == 1, f"Expected a single character, got {ln}"
        self.put(ord(char))

    def put_raw(self, src: Rawish) -> None:
        """Extend `self` from a raw data type source.

        Example
        -------
        ```py
        buffer = BytesMut()
        # A file descriptor's contents
        with open('file.txt', 'rb') as file:
            buffer.put_raw(file)

        # bytes io
        buffer.put(io.BytesIO(b"data"))
        # string io
        buffer.put(io.StringIO("data"))
        ```

        Parameters
        ----------
        src : `Rawish`
            A valid raw data type. See `Rawish` for more details.

        Raises
        ------
        `OverflowError`
            If `src` not in range of `0..255`
        """
        if self._buf is None:
            # If it was `None`, we initialize it with a source instead of extending.
            self._buf = array.array("B", unwrap_bytes(src))
        else:
            self._buf.extend(unwrap_bytes(src))

    def put_bytes(self, src: Buffer) -> None:
        """Put `bytes` into `self`.

        Example
        -------
        ```py
        buf = BytesMut.from_bytes(b"hello")
        buf.put_bytes([32, 119, 111, 114, 108, 100])
        assert buf == b"hello world"
        ```

        Parameters
        ----------
        src : `Buffer`
            Can be one of `Bytes`, `bytes`, `bytearray` or `Sequence[int]`

        Raises
        ------
        `OverflowError`
            If `src` not in range of `0..255`
        """
        if self._buf is None:
            # If it was `None`, we initialize it with a source instead of extending.
            self._buf = array.array("B", src)
        else:
            self._buf.extend(src)

    def put_str(self, s: str) -> None:
        """Put a `utf-8` encoded bytes from a string.

        Example
        -------
        ```py
        buffer = BytesMut()
        buffer.put_str("hello")

        assert buffer == b"hello"
        ```

        Parameters
        ----------
        src: `str`
            The string
        """
        self.put_bytes(s.encode(ENCODING))

    def replace(self, index: int, byte: int) -> None:
        """Replace the byte at `index` with `byte`.

        This method is `NOOP` if:
        -------------------------
        * `self` is empty or unallocated.
        * `index` is out of range.

        Example
        -------
        ```py
        buf = BytesMut.from_bytes([1, 2, 3])
        buf.replace(1, 4)
        assert buf == [1, 4, 3]
        ```
        """
        if not self._buf or index < 0 or index >= self.len():
            return

        self._buf[index] = byte

    def replace_with(self, index: int, f: collections.Callable[[int], int]) -> None:
        """Replace the byte at `index` with a byte returned from `f`.

        The signature of `f` is `Fn(int) -> int`, where the argument is the old byte.

        ## This method is `NOOP` if:
        * `self` is empty or unallocated.
        * `index` is out of range.

        Example
        -------
        ```py
        buf = BytesMut.from_bytes([1, 2, 3])
        buf.replace_with(1, lambda prev: prev * 2)
        assert buf == [1, 4, 3]
        ```
        """
        if not self._buf or index < 0 or index >= self.len():
            return

        old = self._buf[index]
        self._buf[index] = f(old)

    def offset(self, f: collections.Callable[[int], int]) -> None:
        """Modify each byte in the buffer with a new byte returned from `f`.

        The signature of `f` is `Fn(int) -> int`, where the argument is the previous byte.

        Example
        -------
        ```py
        buf = BytesMut.from_bytes([1, 2, 3])
        buf.offset(lambda prev: prev * 2)
        assert buf == [2, 4, 6]
        ```

        This method is `NOOP` if `self` is empty or unallocated.
        """

        if not self._buf:
            return

        for index in range(len(self._buf)):
            self._buf[index] = f(self._buf[index])

    def fill(self, value: int) -> None:
        """Fills `self` with the given byte.

        Nothing happens if the buffer is empty or unallocated.

        Example
        -------
        ```py
        a = Bytes.from_bytes([0, 1, 2, 3])
        a.fill(0)
        assert a == [0, 0, 0, 0]
        ```
        """
        if not self._buf:
            return

        self.as_mut_ptr()[:] = bytearray([value] * self.len())

    def fill_with(self, f: collections.Callable[[], int]) -> None:
        """Fills `self` with the given byte returned from `f`.

        Nothing happens if the buffer is empty or unallocated.

        Example
        -------
        ```py
        def default() -> int:
            return 0

        a = Bytes.from_bytes([0, 1, 2, 3])
        a.fill_with(default)
        assert a == [0, 0, 0, 0]
        ```
        """
        if not self._buf:
            return

        self.as_mut_ptr()[:] = bytearray([f()] * self.len())

    def swap(self, a: int, b: int):
        """Swap two bytes in the buffer.

        if `a` equals to `b` then it's guaranteed that elements won't change value.

        Example
        -------
        ```py
        buf = Bytes.from_bytes([1, 2, 3, 4])
        buf.swap(0, 3)
        assert buf == [4, 2, 3, 1]
        ```

        Raises
        ------
        IndexError
            If the positions of `a` or `b` are out of index.
        """
        if self[a] == self[b]:
            return

        self[a], self[b] = self[b], self[a]

    def swap_unchecked(self, a: int, b: int):
        """Swap two bytes in the buffer. without checking if `a` == `b`.

        If you care about `a` and `b` equality, see `Bytes.swap`.

        Example
        -------
        ```py
        buf = Bytes.from_bytes([1, 2, 3, 1])
        buf.swap_unchecked(0, 3)
        assert buf == [1, 2, 3, 1]
        ```

        Raises
        ------
        IndexError
            If the positions of `a` or `b` are out of index.
        """
        self[a], self[b] = self[b], self[a]

    def as_mut_ptr(self) -> memoryview[int]:
        """Returns a mutable pointer to the buffer data.

        `pointer` here refers to a `memoryview` object.

        A `BufferError` is raised if the underlying sequence is not initialized.

        Example
        -------
        ```py
        buffer = BytesMut.from_str("ouv")
        ptr = buffer.as_mut_ptr()
        ptr[0] = ord(b'L')
        assert buffer.to_bytes() == b"Luv"
        ```
        """
        return self.__buffer__(512)

    def as_mut(self) -> _slice.SliceMut[int]:
        """Get a mutable reference to the underlying sequence, without copying.

        An empty slice is returned if the underlying sequence is not initialized.

        Example
        -------
        ```py
        buff = BytesMut.from_str("Hello")
        ref = buff.as_mut()
        ref.append(32)
        del ref
        assert buff == b"Hello "
        ```
        """
        if self._buf is not None:
            return _slice.SliceMut(self)

        return _slice.SliceMut([])

    @safe
    def freeze(self) -> Bytes:
        """Convert `self` into an immutable `Bytes`.

        This conversion is zero-cost, meaning it doesn't any _hidden-copy_ operations behind the scenes.
        This consumes `self` and returns a new `Bytes` that points to the same underlying array,

        Notes
        -----
        * If `self` is not initialized, a new empty `Bytes` is returned.
        * `self` will no longer be usable, as it will not point to the underlying array.

        The inverse method of this is `Bytes.to_mut()`

        Example
        -------
        ```py
        def shrink_to(cap: int, buffer: BytesMut) -> Bytes:
            buf.truncate(cap)
            return buf.freeze()

        buffer = BytesMut.from_bytes([32, 23, 34, 65])
        # accessing `buffer` after this is undefined behavior.
        modified = shrink_to(2, buffer)
        assert modified == [32, 23]
        ```
        """
        # SAFETY: `Bytes.leak` returns an empty array
        # if `self` is uninitialized.
        return Bytes.from_ptr_unchecked(self.leak())

    def swap_remove(self, byte: int) -> int:
        """Remove the first appearance of `item` from this buffer and return it.

        Raises
        ------
        * `ValueError`: if `item` is not in this buffer.
        * `MemoryError`: if this buffer hasn't allocated, Aka nothing has been pushed to it.

        Example
        -------
        ```py
        buf = BytesMut.from_bytes([1, 2, 3, 4])
        assert 1 == buf.swap_remove(1)
        assert buf == [2, 3, 4]
        ```
        """
        if self._buf is None:
            raise MemoryError("`self` is unallocated.") from None

        return self._buf.pop(self.index(byte))

    def truncate(self, size: int) -> None:
        """Shortens the bytes, keeping the first `size` elements and dropping the rest.

        Example
        -------
        ```py
        buf = BytesMut.from_bytes([0, 0, 0, 0])
        buf.truncate(1)
        assert buf.len() == 1
        ```
        """
        if not self._buf:
            return

        del self._buf[size:]

    def split_off_mut(self, at: int) -> BytesMut:
        """Split the bytes off at the specified position, returning a new
        `BytesMut` at the range of `[at : len]`, leaving `self` at `[at : bytes_len]`.

        if this bytes is empty, `self` is returned unchanged.

        Example
        -------
        ```py
        origin = BytesMut.from_bytes((1, 2, 3, 4))
        split = origin.split_off_mut(2)

        print(origin, split)  # [1, 2], [3, 4]
        ```

        Raises
        ------
        `IndexError`
            This method will raise if `at` > `len(self)`
        """
        len_ = self.len()
        if at > len_:
            raise IndexError(
                f"the index of `at` ({at}) should be <= than len of `self` ({len_}) "
            ) from None

        if not self._buf:
            return self

        split = BytesMut.from_ptr(self._buf[at:len_])
        del self._buf[at:len_]
        return split

    def split_first_mut(self) -> Option[tuple[int, BytesMut]]:
        """Split the first and rest elements of the bytes, If empty, `None` is returned.

        Returns a tuple of (first, rest) where rest is a mutable sequence.

        Example
        -------
        ```py
        buf = BytesMut.from_bytes([1, 2, 3])
        split = buf.split_first_mut()
        assert split == Some((1, [2, 3]))
        ```
        """
        if not self._buf:
            return _option.NOTHING

        if self.len() == 1:
            return _option.Some((self[0], BytesMut()))

        first = self[0]
        rest = self[1:]
        return _option.Some((first, rest))

    def split_last_mut(self) -> Option[tuple[int, Bytes]]:
        """Returns the last and rest of the elements of the bytes, If `self` is empty, `None` is returned.

        Returns a tuple of (last, rest) where rest is a mutable sequence.

        Example
        -------
        ```py
        buf = BytesMut.from_bytes([0, 1, 2])
        last, elements = buf.split_last_mut().unwrap()
        assert (last, elements) == (2, [0, 1])
        ```
        """
        if not self._buf:
            return _option.NOTHING

        len_ = self.len()
        if len_ == 1:
            return _option.Some((self[0], BytesMut()))

        last = self[-1]
        rest = self[:-1]
        return _option.Some((last, rest))

    def split_at_mut(self, mid: int) -> tuple[BytesMut, BytesMut]:
        """Divide `self` into two at an index.

        The first will contain all bytes from `[0:mid]` excluding `mid` itself.
        and the second will contain the remaining bytes.

        if `mid` > `self.len()`, Then all bytes will be moved to the left,
        returning an empty bytes in right.

        Example
        -------
        ```py
        buffer = BytesMut.from_bytes((1, 2, 3, 4))
        left, right = buffer.split_at_mut(0)
        assert left == [] and right == [1, 2, 3, 4]

        left, right = buffer.split_at_mut(2)
        assert left == [1, 2] and right == [3, 4]
        ```

        The is roughly the implementation
        ```py
        self[0:mid], self[mid:]
        ```
        """
        return self[0:mid], self[mid:]

    # * Layout * #

    def insert(self, index: int, value: int) -> None:
        """Insert a new item with `value` in the buffer before position `index`.

        Negative values are treated as being relative to the end of the buffer.
        """
        if self._buf is None:
            return

        self._buf.insert(index, value)

    def pop(self, i: int = -1) -> Option[int]:
        """Removes the last element from the buffer and returns it, `Some(None)` if it is empty.

        Example
        -------
        ```py
        buf = BytesMut((21, 32, 44))
        assert buf.pop() == Some(44)
        ```
        """
        if not self._buf:
            return _option.NOTHING

        return _option.Some(self._buf.pop(i))

    def remove(self, i: int) -> None:
        """Remove the first appearance of `i` from `self`.

        Example
        ------
        ```py
        buf = BytesMut.from_bytes([1, 1, 2, 3, 4])
        buf.remove(1)
        print(buf) # [1, 2, 3, 4]
        ```
        """
        if not self._buf:
            return

        self._buf.remove(i)

    def clear(self) -> None:
        """Clear the buffer.

        Example
        -------
        ```py
        buf = BytesMut.from_bytes([255])
        buf.clear()

        assert buf.is_empty()
        ```
        """
        if not self._buf:
            return

        del self._buf[:]

    def byteswap(self) -> None:
        """Swap the byte order of the bytes in `self`."""
        if not self._buf:
            return

        self._buf.byteswap()

    def copy(self) -> BytesMut:
        """Create a copy of the bytes.

        Example
        -------
        ```py
        original = BytesMut.from_bytes([255, 255, 255, 0])
        copy = original.copy()
        ```
        """
        if not self._buf:
            return BytesMut()

        return self.from_ptr(self._buf[:])

    def __setitem__(self, index: int, value: int):
        if not self._buf:
            raise IndexError("index out of range")

        self._buf[index] = value

    def __delitem__(self, key: typing.SupportsIndex | slice, /) -> None:
        if not self._buf:
            raise IndexError("index out of range")

        del self._buf[key]

    @typing.overload
    def __getitem__(self, index: slice) -> BytesMut: ...

    @typing.overload
    def __getitem__(self, index: int) -> int: ...

    @safe
    def __getitem__(self, index: int | slice) -> int | BytesMut:
        if not self._buf:
            raise IndexError("index out of range")

        if isinstance(index, slice):
            # SAFETY: `self._buf` is initialized.
            return self.from_ptr_unchecked(self._buf[index])

        return self._buf[index]

    @safe
    def __copy__(self) -> BytesMut:
        if not self._buf:
            return BytesMut()

        return BytesMut.from_ptr_unchecked(self._buf.__copy__())

    @safe
    def __deepcopy__(self, unused: typing.Any, /) -> BytesMut:
        if not self._buf:
            return BytesMut()

        return BytesMut.from_ptr_unchecked(self._buf.__deepcopy__(unused))
