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
"""The default trait for types that can have a default implementation.

Example
-------
```py

from sain import Default

class Generator(Default[str]):
    @staticmethod
    def default() -> str:
        return generator.random_str()

DEFAULT_GENERATOR = Generator.default()
```
"""

from __future__ import annotations

__all__ = ("Default",)

import typing

from .macros import rustc_diagnostic_item

_T_co = typing.TypeVar("_T_co", covariant=True)


@rustc_diagnostic_item("Default")
@typing.runtime_checkable
class Default(typing.Protocol[_T_co]):
    """An interface for an object that has a default value.

    Example
    -------
    ```py
    from sain import Default

    class Cache(Default[dict[str, Any]]):

        @staticmethod
        def default() -> dict[str, Any]:
            return {}

    cache = Cache.default()
    print(cache)
    assert isinstance(cache, Default)
    # {}
    ```
    """

    __slots__ = ()

    # FIXME: `impl Default for String` knows the type of `Self` is `String` but we can't do that.
    # So generics is the only way to achieve the same effect. But `Default` in Rust is not generic.
    # in the future we just swap to `Self`.
    @rustc_diagnostic_item("default_fn")
    @staticmethod
    def default() -> _T_co:
        """Return the default value of the object."""
        raise NotImplementedError
