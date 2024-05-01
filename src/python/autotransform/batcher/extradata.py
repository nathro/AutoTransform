# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the ExtraDataBatcher."""

from collections import defaultdict
from typing import Any, ClassVar, Dict, List, Sequence

from autotransform.batcher.base import Batch, Batcher, BatcherName
from autotransform.item.base import Item
from pydantic import Field


class ExtraDataBatcher(Batcher):
    """A Batcher which uses the extra data on Items to create batches.

    Attributes:
        group_by (str): The key of the extra_data on items to group Items by for Batches.
        metadata_keys (optional, List[str]): A list of keys from Items to combine in to the
            metadata of a batch. Defaults to [].

        name (ClassVar[BatcherName]): The name of the Component.
    """

    group_by: str
    metadata_keys: List[str] = Field(default_factory=list)

    name: ClassVar[BatcherName] = BatcherName.EXTRA_DATA

    def batch(self, items: Sequence[Item]) -> List[Batch]:
        """Take filtered Items and group them by an extra_data value.

        Args:
            items (Sequence[Item]): The filtered Items to separate.

        Returns:
            List[Batch]: A list of Batches grouped by the extra_data of the Items.
        """

        groups: Dict[str, List[Item]] = defaultdict(list)
        for item in items:
            extra_data = item.extra_data or {}
            group_by_val = extra_data[self.group_by]
            assert isinstance(group_by_val, str), "Group by values must be strings"
            groups[group_by_val].append(item)

        batches: List[Batch] = []
        for group_title, group_items in groups.items():
            batch: Batch = {"items": group_items, "title": group_title}
            if self.metadata_keys:
                metadata: Dict[str, List[Any]] = {
                    key: []
                    for key in self.metadata_keys  # pylint: disable=not-an-iterable
                }
                for item in group_items:
                    extra_data = item.extra_data or {}
                    for key in self.metadata_keys:  # pylint: disable=not-an-iterable
                        val = extra_data.get(key)
                        if isinstance(val, list):
                            metadata[key].extend(val)
                        elif val is not None:
                            metadata[key].append(val)
                batch["metadata"] = {
                    key: list(set(values)) for key, values in metadata.items()
                }
            batches.append(batch)
        return batches
