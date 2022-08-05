# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for inline Inputs."""

from __future__ import annotations

from typing import Any, ClassVar, Dict, List, Sequence, Type

from autotransform.input.base import Input, InputName
from autotransform.item.base import FACTORY as item_factory
from autotransform.item.base import Item
from autotransform.item.file import FileItem


class InlineInput(Input):
    """An Input that simply returns the supplied Items as input.

    Attributes:
        items (List[Item]): The items to return.
        name (ClassVar[InputName]): The name of the component.
    """

    items: List[Item]

    name: ClassVar[InputName] = InputName.INLINE

    def get_items(self) -> Sequence[Item]:
        """Returns the supplied Items as input.

        Returns:
            Sequence[Item]: The supplied Items.
        """

        return self.items

    @classmethod
    def from_data(cls: Type[InlineInput], data: Dict[str, Any]) -> InlineInput:
        """Produces an instance of the component from decoded data.

        Args:
            data (Dict[str, Any]): The JSON decoded data.

        Returns:
            InlineInput: An instance of the component.
        """

        return cls(items=[item_factory.get_instance(item) for item in data["items"]])


class InlineFileInput(Input):
    """An Input that simply returns the supplied file paths as FileItems for input.

    Attributes:
        files (List[str]): The file paths for Items to return.
        name (ClassVar[InputName]): The name of the component.
    """

    files: List[str]

    name: ClassVar[InputName] = InputName.INLINE_FILE

    def get_items(self) -> Sequence[FileItem]:
        """Returns the supplied files as FileItems for input.

        Returns:
            Sequence[FileItem]: The supplied files as FileItems.
        """

        return [FileItem(key=file) for file in self.files]


class InlineGenericInput(Input):
    """An Input that simply returns the supplied keys as Items for input.

    Attributes:
        keys (List[str]): The keys for Items to return.
        name (ClassVar[InputName]): The name of the component.
    """

    keys: List[str]

    name: ClassVar[InputName] = InputName.INLINE_GENERIC

    def get_items(self) -> Sequence[Item]:
        """Returns the supplied keys as Items for input.

        Returns:
            Sequence[Item]: The supplied keys as Items.
        """

        return [Item(key=key) for key in self.keys]
