# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Batcher components."""

from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import Any, ClassVar, List, Mapping, Sequence, TypedDict

from typing_extensions import NotRequired

from autotransform.item.base import Item
from autotransform.util.component import NamedComponent, ComponentFactory, ComponentImport


class BatcherName(str, Enum):
    """A simple enum for mapping."""

    CHUNK = "chunk"
    DIRECTORY = "directory"
    SINGLE = "single"


class Batch(TypedDict):
    """A logical grouping of Items with title and associated metadata."""

    items: Sequence[Item]
    metadata: NotRequired[Mapping[str, Any]]
    title: str


class Batcher(NamedComponent):
    """The base for Batcher components. Used by AutoTransform to separate Items in to logical
    groupings that can be acted on indepently and have associated metadata.

    Attributes:
        name (ClassVar[BatcherName]): The name of the Component.
    """

    name: ClassVar[BatcherName]

    @abstractmethod
    def batch(self, items: Sequence[Item]) -> List[Batch]:
        """Take filtered Items and separate in to logical groupings with associated group metadata
        and title.

        Args:
            items (Sequence[Item]): The filtered Items to separate.

        Returns:
            List[Batch]: A list of logical groupings of Items with associated group metadata and
                title.
        """


FACTORY = ComponentFactory(
    {
        BatcherName.CHUNK: ComponentImport(
            class_name="ChunkBatcher", module="autotransform.batcher.chunk"
        ),
        BatcherName.DIRECTORY: ComponentImport(
            class_name="DirectoryBatcher", module="autotransform.batcher.directory"
        ),
        BatcherName.SINGLE: ComponentImport(
            class_name="SingleBatcher", module="autotransform.batcher.single"
        ),
    },
    Batcher,  # type: ignore [misc]
    "batcher.json",
)
