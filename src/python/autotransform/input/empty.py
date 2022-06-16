# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the EmptyInput."""

from __future__ import annotations

from typing import ClassVar, Sequence

from autotransform.input.base import Input, InputName
from autotransform.item.base import Item


class EmptyInput(Input):
    """An Input that simply returns an empty list. Used when a Transformer operates
    on the whole codebase, rather than on an individual Item/set of Items.

    Attributes:
        name (ClassVar[InputName]): The name of the component.
    """

    name: ClassVar[InputName] = InputName.EMPTY

    def get_items(self) -> Sequence[Item]:
        """Returns an empty list of Items, useful for Transformers that operate
        on the whole codebase at once.

        Returns:
            Sequence[Item]: An empty list of Items.
        """
        return []
