# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the SingleBatcher."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence, TypedDict

from typing_extensions import NotRequired

from autotransform.batcher.base import Batch, Batcher
from autotransform.batcher.type import BatcherType
from autotransform.item.base import Item


class SingleBatcherParams(TypedDict):
    """The param type for a SingleBatcher."""

    metadata: NotRequired[Mapping[str, Any]]
    title: str


class SingleBatcher(Batcher[SingleBatcherParams]):
    """A batcher which puts all Items together in to a single batch

    Attributes:
        _params (SingleBatcherParams): Contains the batch title and any needed metadata.
    """

    _params: SingleBatcherParams

    @staticmethod
    def get_type() -> BatcherType:
        """Used to map Batcher components 1:1 with an enum, allowing construction from JSON.

        Returns:
            BatcherType: The unique type associated with this Batcher
        """

        return BatcherType.SINGLE

    def batch(self, items: Sequence[Item]) -> List[Batch]:
        """Takes in a list Items and batches them together in to a single Batch.

        Args:
            items (Sequence[Item]): The filtered Items to separate.

        Returns:
            List[Batch]: A list containing a single Batch for all Items.
        """

        batch: Batch = {
            "items": items,
            "title": self._params["title"],
        }
        if "metadata" in self._params:
            batch["metadata"] = self._params["metadata"]
        return [batch]

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> SingleBatcher:
        """Produces a SingleBatcher from the provided data.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            SingleBatcher: An instance of the SingleBatcher with the provided params.
        """

        title = data["title"]
        assert isinstance(title, str)
        params: SingleBatcherParams = {
            "title": title,
        }
        metadata = data.get("metadata", None)
        if metadata is not None:
            assert isinstance(metadata, Dict)
            params["metadata"] = metadata

        return SingleBatcher(params)
