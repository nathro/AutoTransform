# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the ChunkBatcher."""

from __future__ import annotations

from copy import deepcopy
from math import ceil
from typing import Any, ClassVar, Dict, List, Optional, Sequence

from autotransform.batcher.base import Batch, Batcher, BatcherName
from autotransform.item.base import Item


class ChunkBatcher(Batcher):
    """A batcher which chunks Items in to several Batches. A chunk size is supplied that
    determines the size of Batches. A maximum number of chunks can optionally be supplied. If
    the chunk size would result in more than the maximum number of chunks, the chunk size is
    increased to the minimum required to create only max_chunks. The title for a batch will
    have [X/N] prepended to it, where X represents the chunk number and N represents the
    total number of chunks.

    Attributes:
        chunk_size (int): The size of chunks.
        title (str): The title to use for Batches.
        max_chunks (Optional[int], optional): The maximum number of chunks to create. Defaults
            to None.
        metadata (Optional[Dict[str, Any]], optional): The metadata to associate with
            Batches. Defaults to None.
        name (ClassVar[BatcherName]): The name of the Component.
    """

    chunk_size: int
    title: str
    max_chunks: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

    name: ClassVar[BatcherName] = BatcherName.CHUNK

    def batch(self, items: Sequence[Item]) -> List[Batch]:
        """Take filtered Items and chunk them into Batches.

        Args:
            items (Sequence[Item]): The filtered Items to separate.

        Returns:
            List[Batch]: A list of Batches representing each chunk of the filtered
                Items.
        """

        # Ensure no more than max chunks
        chunk_size = self.chunk_size
        if self.max_chunks is not None and len(items) / chunk_size > self.max_chunks:
            chunk_size = ceil(len(items) / self.max_chunks)

        # Create Batches
        item_chunks = [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]
        item_batches: List[Batch] = []
        for idx, item_chunk in enumerate(item_chunks, start=1):
            title = f"[{idx}/{len(item_chunks)}] " + self.title
            batch: Batch = {"items": item_chunk, "title": title}
            if self.metadata is not None:
                # Deepcopy metadata to ensure mutations don't apply to all Batches
                batch["metadata"] = deepcopy(self.metadata)
            item_batches.append(batch)
        return item_batches
