# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the DirectoryBatcher."""

from __future__ import annotations

import pathlib
from copy import deepcopy
from typing import Any, ClassVar, Dict, List, Optional, Sequence

from autotransform.batcher.base import Batch, Batcher, BatcherName
from autotransform.item.base import Item
from autotransform.item.file import FileItem


class DirectoryBatcher(Batcher):
    """A batcher which separates FileItems by directory. Batches are given a title that is based
    on a prefix and the directory that the Batch represents.

    Attributes:
        prefix (str): The prefix to apply to any titles for Batches.
        metadata (Optional[Dict[str, Any]], optional): The metadata to associate with
            Batches. Defaults to None.
        name (ClassVar[BatcherName]): The name of the Component.
    """

    prefix: str
    metadata: Optional[Dict[str, Any]] = None

    name: ClassVar[BatcherName] = BatcherName.DIRECTORY

    def batch(self, items: Sequence[Item]) -> List[Batch]:
        """Takes in a list of FileItems and separates them based on their directory.

        Args:
            items (Sequence[Item]): The filtered Items to separate.

        Returns:
            List[Batch]: A list containing a Batch for each directory containing files.
        """

        # Get a mapping from directory to items within that directory
        item_map: Dict[str, List[FileItem]] = {}
        for item in items:
            assert isinstance(item, FileItem)
            directory = str(pathlib.Path(item.get_path()).parent).replace("\\", "/")
            if directory not in item_map:
                item_map[directory] = []
            item_map[directory].append(item)

        # Create Batches
        batches: List[Batch] = [
            {"items": batch_items, "title": self.prefix + ": " + directory}
            for directory, batch_items in item_map.items()
        ]

        if self.metadata is not None:
            for batch in batches:
                # Deepcopy metadata to ensure mutations don't apply to all Batches
                batch["metadata"] = deepcopy(self.metadata)
        return batches
