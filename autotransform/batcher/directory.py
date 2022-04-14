# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the directory Batcher."""

from __future__ import annotations

import pathlib
from typing import Any, Dict, List, Mapping, TypedDict

from autotransform.batcher.base import Batch, Batcher
from autotransform.batcher.type import BatcherType
from autotransform.util.cachedfile import CachedFile


class DirectoryBatcherParams(TypedDict):
    """The param type for a DirectoryBatcher. Includes a prefix that's added to the
    front of the directory to create a title.
    """

    prefix: str


class DirectoryBatcher(Batcher[DirectoryBatcherParams]):
    """A batcher which puts separates inputs in to batches based on directory.

    Attributes:
        params (DirectoryBatcherParams): Contains the metadata to associate with the Batch
    """

    params: DirectoryBatcherParams

    def get_type(self) -> BatcherType:
        """Used to map Batcher components 1:1 with an enum, allowing construction from JSON.

        Returns:
            BatcherType: The unique type associated with this Batcher
        """
        return BatcherType.DIRECTORY

    def batch(self, files: List[CachedFile]) -> List[Batch]:
        """Takes in a list of input files and produces a batch for each directory.
        The last folder containing the file is used as the key for batching.

        Args:
            files (List[CachedFile]): The filtered input files.

        Returns:
            List[Batch]: A list containing a batch for each folder containing files
        """
        batches: Dict[str, List[CachedFile]] = {}
        for file in files:
            directory = str(pathlib.Path(file.path).parent).replace("\\", "/")
            if directory not in batches:
                batches[directory] = []
            batches[directory].append(file)
        return [
            {"files": files, "metadata": {"title": self.params["prefix"] + ": " + directory}}
            for directory, files in batches.items()
        ]

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> DirectoryBatcher:
        """Takes in decoded param data and produces a DirectoryBatcher component after
        validating the data.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle

        Returns:
            DirectoryBatcher: An instance of the DirectoryBatcher
        """

        prefix = data["prefix"]
        assert isinstance(prefix, str)
        return DirectoryBatcher({"prefix": prefix})
