# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the DirectoryInput."""

from __future__ import annotations

from typing import Any, Mapping, Sequence, TypedDict

from autotransform.input.base import Input
from autotransform.input.type import InputType
from autotransform.item.base import Item


class EmptyInputParams(TypedDict):
    """The param type for a EmptyInput."""


class EmptyInput(Input[EmptyInputParams]):
    """An Input that simply returns an empty list. Used when a Transformer operates
    on the whole codebase, rather than on an individual Item/set of Items.

    Attributes:
        _params (EmptyInputParams): Contains the directory to walk.
    """

    _params: EmptyInputParams

    @staticmethod
    def get_type() -> InputType:
        """Used to map Input components 1:1 with an enum, allowing construction from JSON.

        Returns:
            InputType: The unique type associated with this Input.
        """
        return InputType.EMPTY

    def get_items(self) -> Sequence[Item]:
        """Returns an empty list of Items, useful for Transformers that operate
        on the whole codebase at once.

        Returns:
            Sequence[Item]: An empty list of Items.
        """
        return []

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> EmptyInput:
        """Produces an EmptyInput from the provided data.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            EmptyInput: An instance of the EmptyInput with the provided params.
        """

        return EmptyInput({})
