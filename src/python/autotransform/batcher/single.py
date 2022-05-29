# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the SingleBatcher."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Sequence

from autotransform.batcher.base import Batch, Batcher, BatcherName
from autotransform.item.base import Item
from autotransform.util.component import ComponentParams


@dataclass
class SingleBatcherParams(ComponentParams):
    """The param type for a SingleBatcher."""

    title: str
    metadata: Optional[Mapping[str, Any]] = None
    skip_empty_batch: bool = False


class SingleBatcher(Batcher[SingleBatcherParams]):
    """A batcher which puts all Items together in to a single batch

    Attributes:
        _params (SingleBatcherParams): Contains the batch title and any needed metadata.
    """

    _params: SingleBatcherParams

    @staticmethod
    def get_name() -> BatcherName:
        """Used to map Batcher components 1:1 with an enum, allowing construction from JSON.

        Returns:
            BatcherName: The unique name associated with this Batcher.
        """

        return BatcherName.SINGLE

    def batch(self, items: Sequence[Item]) -> List[Batch]:
        """Takes in a list Items and batches them together in to a single Batch.

        Args:
            items (Sequence[Item]): The filtered Items to separate.

        Returns:
            List[Batch]: A list containing a single Batch for all Items.
        """
        if self._params.skip_empty_batch and len(items) == 0:
            return []

        batch: Batch = {
            "items": items,
            "title": self._params.title,
        }
        if self._params.metadata is not None:
            batch["metadata"] = deepcopy(self._params.metadata)
        return [batch]

    @staticmethod
    def from_data(data: Dict[str, Any]) -> SingleBatcher:
        """Produces a SingleBatcher from the provided data.

        Args:
            bundle (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            SingleBatcher: An instance of the SingleBatcher with the provided params.
        """

        return SingleBatcher(SingleBatcherParams.from_data(data))
