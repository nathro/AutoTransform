# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""An interface for Transformers that operate on single Items with no metadata needs."""


from abc import abstractmethod

from autotransform.batcher.base import Batch
from autotransform.item.base import Item
from autotransform.transformer.base import Transformer


class SingleTransformer(Transformer[None]):
    """A simple interface for writing a Transformer that operates on an individual Item level."""

    @abstractmethod
    def _transform_item(self, item: Item) -> None:
        """Executes a transformation on a single Item.

        Args:
            item (Item): The Item that is being transformed.
        """

    def transform(self, batch: Batch) -> None:
        """Splits out all Items to be transformed.

        Args:
            batch (Batch): The Batch being transformed.
        """

        for item in batch["items"]:
            self._transform_item(item)
