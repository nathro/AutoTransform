# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The implementation for the chunk Batcher."""

from __future__ import annotations

from copy import deepcopy
from math import ceil
from typing import Any, Dict, List, Mapping, TypedDict

from typing_extensions import NotRequired

from autotransform.batcher.base import Batch, Batcher, BatchMetadata
from autotransform.batcher.type import BatcherType
from autotransform.common.cachedfile import CachedFile


class ChunkBatcherParams(TypedDict):
    """The param type for a ChunkBatcher."""

    metadata: BatchMetadata
    chunk_size: int
    max_chunks: NotRequired[int]


class ChunkBatcher(Batcher[ChunkBatcherParams]):
    """A batcher which puts chunks inputs in to several batches. A chunk size is supplied that
    determines the size of batches. A maximum number of chunks can optionally be supplied. If
    the chunk size would result in more than the maximum number of chunks, the chunk size is
    increased to the minimum required to create only max_chunks. The title in metadata will
    have [X/N] prepended to it, where X represents the chunk number and N represents the
    total number of chunks.

    Attributes:
        params (ChunkBatcherParams): Contains the metadata to associate with the Batch
    """

    params: ChunkBatcherParams

    def get_type(self) -> BatcherType:
        """Used to map Batcher components 1:1 with an enum, allowing construction from JSON.

        Returns:
            BatcherType: The unique type associated with this Batcher
        """
        return BatcherType.CHUNK

    def batch(self, files: List[CachedFile]) -> List[Batch]:
        """Takes in a list of input files and separates them in to batches

        Args:
            files (List[CachedFile]): The filtered input files.

        Returns:
            List[Batch]: A list containing a single batch for the input
        """
        chunk_size = self.params["chunk_size"]
        if "max_chunks" in self.params and len(files) / chunk_size > self.params["max_chunks"]:
            chunk_size = ceil(len(files) / self.params["max_chunks"])
        file_chunks = [files[i : i + chunk_size] for i in range(0, len(files), chunk_size)]
        file_batches: List[Batch] = []
        for idx, file_chunk in enumerate(file_chunks, start=1):
            metadata = deepcopy(self.params["metadata"])
            metadata["title"] = f"[{idx}/{len(file_chunks)}] " + metadata["title"]
            file_batches.append({"files": file_chunk, "metadata": metadata})
        return file_batches

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> ChunkBatcher:
        """Takes in decoded param data and produces a ChunkBatcher component after
        validating the data.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle

        Returns:
            ChunkBatcher: An instance of the ChunkBatcher
        """

        assert isinstance(data["metadata"], Dict)
        assert isinstance(data["metadata"]["title"], str)
        assert isinstance(data["chunk_size"], int)
        if "max_chunks" in data:
            assert isinstance(data["max_chunks"], int)

        return ChunkBatcher(data)  # type: ignore
