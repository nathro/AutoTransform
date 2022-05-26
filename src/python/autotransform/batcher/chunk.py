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
from math import ceil
from typing import Any, Dict, List, Mapping, Sequence, TypedDict

from typing_extensions import NotRequired

from autotransform.batcher.base import Batch, Batcher
from autotransform.batcher.type import BatcherType
from autotransform.item.base import Item


class ChunkBatcherParams(TypedDict):
    """The param type for a ChunkBatcher."""

    chunk_size: int
    max_chunks: NotRequired[int]
    metadata: NotRequired[Mapping[str, Any]]
    title: str


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
    def get_type() -> BatcherType:
        """Used to map Batcher components 1:1 with an enum, allowing construction from JSON.

        Returns:
            BatcherType: The unique type associated with this Batcher.
        """

        return BatcherType.CHUNK

    def batch(self, items: Sequence[Item]) -> List[Batch]:
        """Take filtered Items and chunk them into Batches.

        Args:
            items (Sequence[Item]): The filtered Items to separate.

        Returns:
            List[Batch]: A list of logical groupings of Items with associated group metadata and
                title.
        """

        chunk_size = self._params["chunk_size"]
        if "max_chunks" in self._params and len(items) / chunk_size > self._params["max_chunks"]:
            chunk_size = ceil(len(items) / self._params["max_chunks"])
        item_chunks = [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]
        item_batches: List[Batch] = []
        for idx, item_chunk in enumerate(item_chunks, start=1):
            title = f"[{idx}/{len(item_chunks)}] " + self._params["title"]
            batch: Batch = {"items": item_chunk, "title": title}
            metadata = self._params.get("metadata", None)
            if metadata is not None:
                batch["metadata"] = deepcopy(metadata)
            item_batches.append(batch)
        return item_batches

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> ChunkBatcher:
        """Produces a ChunkBatcher from the provided data.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle

        Returns:
            ChunkBatcher: An instance of the ChunkBatcher with the provided params.
        """

        title = data["title"]
        assert isinstance(title, str)
        chunk_size = data["chunk_size"]
        assert isinstance(chunk_size, int)
        params: ChunkBatcherParams = {
            "title": title,
            "chunk_size": chunk_size,
        }
        metadata = data.get("metadata", None)
        if metadata is not None:
            assert isinstance(data["metadata"], Dict)
            params["metadata"] = metadata
        max_chunks = data.get("max_chunks", None)
        if max_chunks is not None:
            assert isinstance(max_chunks, int)
            params["max_chunks"] = max_chunks

        return ChunkBatcher(params)
