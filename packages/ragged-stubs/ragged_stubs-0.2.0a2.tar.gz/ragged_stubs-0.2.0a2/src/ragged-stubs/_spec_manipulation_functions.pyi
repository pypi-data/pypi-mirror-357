# Copyright 2025 hingebase

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from collections.abc import Sequence
from typing import Any, TypeVar

from ._spec_array_object import array
from ._typing import Dtype

def broadcast_arrays(
    arrays: array[Any, _DTypeT],
) -> list[array[Any, _DTypeT]]: ...
def broadcast_to(
    x: array[Any, _DTypeT],
    /,
    shape: int | tuple[int, ...],
) -> array[Any, _DTypeT]: ...
def concat(arrays: Sequence[array], /, *, axis: int | None = ...) -> array: ...
def expand_dims(
    x: array[Any, _DTypeT],
    /,
    *,
    axis: int = ...,
) -> array[Any, _DTypeT]: ...
def flip(
    x: array[Any, _DTypeT],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
) -> array[Any, _DTypeT]: ...
def permute_dims(
    x: array[Any, _DTypeT],
    /,
    axes: tuple[int, ...],
) -> array[Any, _DTypeT]: ...
def reshape(
    x: array[Any, _DTypeT],
    /,
    shape: int | tuple[int, ...],
    *,
    copy: bool | None = ...,
) -> array[Any, _DTypeT]: ...
def roll(
    x: array[Any, _DTypeT],
    /,
    shift: int | tuple[int, ...],
    *,
    axis: int | tuple[int, ...] | None = ...,
) -> array[Any, _DTypeT]: ...
def squeeze(
    x: array[Any, _DTypeT],
    /,
    axis: int | tuple[int, ...],
) -> array[Any, _DTypeT]: ...
def stack(arrays: Sequence[array], /, *, axis: int = ...) -> array: ...

_DTypeT = TypeVar("_DTypeT", bound=Dtype)
