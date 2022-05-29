# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the chunk Batcher."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from math import ceil
from typing import Any, Dict, List, Mapping, Optional, Sequence

from autotransform.batcher.base import Batch, Batcher, BatcherName
from autotransform.item.base import Item
from autotransform.util.component import ComponentParams


@dataclass
class ChunkBatcherParams(ComponentParams):
    """The param type for a ChunkBatcher."""

    chunk_size: int
    title: str
    max_chunks: Optional[int] = None
    metadata: Optional[Mapping[str, Any]] = None


class ChunkBatcher(Batcher[ChunkBatcherParams]):
    """A batcher which chunks Items in to several Batches. A chunk size is supplied that
    determines the size of Batches. A maximum number of chunks can optionally be supplied. If
    the chunk size would result in more than the maximum number of chunks, the chunk size is
    increased to the minimum required to create only max_chunks. The title for a batch will
    have [X/N] prepended to it, where X represents the chunk number and N represents the
    total number of chunks.

    Attributes:
        _params (ChunkBatcherParams): Contains the chunking information along with metadata
            and title.
    """

    _params: ChunkBatcherParams

    @staticmethod
    def get_name() -> BatcherName:
        """Used to map Batcher components 1:1 with an enum, allowing construction from JSON.

        Returns:
            BatcherName: The unique name associated with this Batcher.
        """

        return BatcherName.CHUNK

    def batch(self, items: Sequence[Item]) -> List[Batch]:
        """Take filtered Items and chunk them into Batches.

        Args:
            items (Sequence[Item]): The filtered Items to separate.

        Returns:
            List[Batch]: A list of logical groupings of Items with associated group metadata and
                title.
        """

        chunk_size = self._params.chunk_size
        if (
            self._params.max_chunks is not None
            and len(items) / chunk_size > self._params.max_chunks
        ):
            chunk_size = ceil(len(items) / self._params.max_chunks)
        item_chunks = [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]
        item_batches: List[Batch] = []
        for idx, item_chunk in enumerate(item_chunks, start=1):
            title = f"[{idx}/{len(item_chunks)}] " + self._params.title
            batch: Batch = {"items": item_chunk, "title": title}
            if self._params.metadata is not None:
                batch["metadata"] = deepcopy(self._params.metadata)
            item_batches.append(batch)
        return item_batches

    @staticmethod
    def from_data(data: Dict[str, Any]) -> ChunkBatcher:
        """Produces a ChunkBatcher from the provided data.

        Args:
            bundle (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            ChunkBatcher: An instance of the ChunkBatcher with the provided params.
        """

        return ChunkBatcher(ChunkBatcherParams.from_data(data))
