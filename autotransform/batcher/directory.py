# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the directory Batcher."""

from __future__ import annotations

import pathlib
from typing import Any, Dict, List, Mapping, Sequence, TypedDict

from typing_extensions import NotRequired

from autotransform.batcher.base import Batch, Batcher
from autotransform.batcher.type import BatcherType
from autotransform.item.base import Item
from autotransform.item.file import FileItem


class DirectoryBatcherParams(TypedDict):
    """The param type for a DirectoryBatcher."""

    metadata: NotRequired[Mapping[str, Any]]
    prefix: str


class DirectoryBatcher(Batcher[DirectoryBatcherParams]):
    """A batcher which separates FileItems by directory. Batches are given a title that is based
    on a prefix and the directory that the batch is using.

    Attributes:
        _params (DirectoryBatcherParams): Contains the prefix to use for constructing a title.
    """

    _params: DirectoryBatcherParams

    @staticmethod
    def get_type() -> BatcherType:
        """Used to map Batcher components 1:1 with an enum, allowing construction from JSON.

        Returns:
            BatcherType: The unique type associated with this Batcher.
        """

        return BatcherType.DIRECTORY

    def batch(self, items: Sequence[Item]) -> List[Batch]:
        """Takes in a list FileItems and separates them based on their directory.

        Args:
            items (Sequence[Item]): The filtered Items to separate.

        Returns:
            List[Batch]: A list containing a batch for each folder containing files.
        """

        item_map: Dict[str, List[FileItem]] = {}
        for item in items:
            assert isinstance(item, FileItem)
            directory = str(pathlib.Path(item.get_path()).parent).replace("\\", "/")
            if directory not in item_map:
                item_map[directory] = []
            item_map[directory].append(item)

        batches: List[Batch] = [
            {"items": batch_items, "title": self._params["prefix"] + ": " + directory}
            for directory, batch_items in item_map.items()
        ]

        if "metadata" in self._params:
            for batch in batches:
                batch["metadata"] = self._params["metadata"]
        return batches

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> DirectoryBatcher:
        """Produces a DirectoryBatcher from the provided data.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle

        Returns:
            DirectoryBatcher: An instance of the DirectoryBatcher with the provided params.
        """

        prefix = data["prefix"]
        assert isinstance(prefix, str)
        params: DirectoryBatcherParams = {
            "prefix": prefix,
        }
        metadata = data.get("metadata", None)
        if metadata is not None:
            assert isinstance(metadata, Dict)
            params["metadata"] = metadata
        return DirectoryBatcher(params)
