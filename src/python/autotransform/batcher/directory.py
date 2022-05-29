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
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Sequence

from autotransform.batcher.base import Batch, Batcher, BatcherName
from autotransform.item.base import Item
from autotransform.item.file import FileItem
from autotransform.util.component import ComponentParams


@dataclass
class DirectoryBatcherParams(ComponentParams):
    """The param type for a DirectoryBatcher."""

    prefix: str
    metadata: Optional[Mapping[str, Any]] = None


class DirectoryBatcher(Batcher[DirectoryBatcherParams]):
    """A batcher which separates FileItems by directory. Batches are given a title that is based
    on a prefix and the directory that the batch is using.

    Attributes:
        _params (DirectoryBatcherParams): Contains the prefix to use for constructing a title.
    """

    _params: DirectoryBatcherParams

    @staticmethod
    def get_name() -> BatcherName:
        """Used to map Batcher components 1:1 with an enum, allowing construction from JSON.

        Returns:
            BatcherName: The unique name associated with this Batcher.
        """

        return BatcherName.DIRECTORY

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
            {"items": batch_items, "title": self._params.prefix + ": " + directory}
            for directory, batch_items in item_map.items()
        ]

        if self._params.metadata is not None:
            for batch in batches:
                batch["metadata"] = deepcopy(self._params.metadata)
        return batches

    @staticmethod
    def from_data(data: Dict[str, Any]) -> DirectoryBatcher:
        """Produces a DirectoryBatcher from the provided data.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle

        Returns:
            DirectoryBatcher: An instance of the DirectoryBatcher with the provided params.
        """

        return DirectoryBatcher(DirectoryBatcherParams.from_data(data))
