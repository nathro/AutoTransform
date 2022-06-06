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
from typing import Any, ClassVar, Dict, List, Optional, Sequence

from autotransform.batcher.base import Batch, Batcher, BatcherName
from autotransform.item.base import Item


class SingleBatcher(Batcher):
    """A batcher which puts all Items together in to a single batch

    Attributes:
        title (str): The title to use for the Batch.
        metadata (Optional[Dict[str, Any]], optional): The metadata to use for the
            Batch. Defaults to None.
        metadata (Optional[Dict[str, Any]], optional): The metadata to associate with
            the Batch. Defaults to None.
        name (ClassVar[BatcherName]): The name of the Component.
    """

    title: str
    metadata: Optional[Dict[str, Any]] = None
    skip_empty_batch: bool = False

    name: ClassVar[BatcherName] = BatcherName.SINGLE

    def batch(self, items: Sequence[Item]) -> List[Batch]:
        """Takes in a list Items and batches them together in to a single Batch.

        Args:
            items (Sequence[Item]): The filtered Items to separate.

        Returns:
            List[Batch]: A list containing a single Batch for all Items.
        """
        if self.skip_empty_batch and len(items) == 0:
            return []

        batch: Batch = {
            "items": items,
            "title": self.title,
        }
        if self.metadata is not None:
            batch["metadata"] = deepcopy(self.metadata)
        return [batch]
