# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The implementation for the single Batcher."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, TypedDict

from autotransform.batcher.base import Batch, Batcher, BatchMetadata
from autotransform.batcher.type import BatcherType
from autotransform.common.cachedfile import CachedFile


class SingleBatcherParams(TypedDict):
    """The param type for a SingleBatcher."""

    metadata: BatchMetadata


class SingleBatcher(Batcher):
    """A batcher which puts all inputs together in to a single Batch.

    Attributes:
        params (SingleBatcherParams): Contains the metadata to associate with the Batch
    """

    params: SingleBatcherParams

    def get_type(self) -> BatcherType:
        """Used to map Batcher components 1:1 with an enum, allowing construction from JSON.

        Returns:
            BatcherType: The unique type associated with this Batcher
        """
        return BatcherType.SINGLE

    def batch(self, files: List[CachedFile]) -> List[Batch]:
        """Takes in a list of input files and produces a single Batch from them.
        Uses the metadata stored in params as the metadata for the Batch.

        Args:
            files (List[CachedFile]): The filtered input files.

        Returns:
            List[Batch]: A list containing a single batch for the input
        """
        batch: Batch = {
            "files": files,
            "metadata": self.params["metadata"],
        }
        return [batch]

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> SingleBatcher:
        """Takes in decoded param data and produces a SingleBatcher component after
        validating the data.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle

        Returns:
            SingleBatcher: An instance of the SingleBatcher
        """

        metadata = data["metadata"]
        assert isinstance(metadata, Dict)
        title = metadata["title"]
        assert isinstance(title, str)
        if "summary" in metadata:
            summary = metadata["summary"]
            assert isinstance(summary, str)
        else:
            summary = None
        if "tests" in metadata:
            tests = metadata["tests"]
            assert isinstance(tests, str)
        else:
            tests = None
        return SingleBatcher(
            {
                "metadata": {
                    "title": title,
                    "summary": summary,
                    "tests": tests,
                }
            }
        )
