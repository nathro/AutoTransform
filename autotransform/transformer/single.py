# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""An interface for transformers that operate on single files with no metadata needs."""


from abc import abstractmethod
from typing import Any, Generic, Mapping, TypeVar

from autotransform.batcher.base import Batch
from autotransform.item.base import Item
from autotransform.transformer.base import Transformer

TParams = TypeVar("TParams", bound=Mapping[str, Any])


class SingleTransformer(Generic[TParams], Transformer[TParams]):
    """A simple interface for writing a transformer that operates on an individual file level."""

    @abstractmethod
    def _transform_item(self, item: Item) -> None:
        """Executes a transformation on a single Item.

        Args:
            item (Item): The Item that is being transformed.
        """

    def transform(self, batch: Batch) -> None:
        """Splits out all files to be transformed.

        Args:
            batch (Batch): The batch being transformed
        """

        for item in batch["items"]:
            self._transform_item(item)
