# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the RegexBatcher."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any, ClassVar, Dict, List, Sequence

from autotransform.batcher.base import Batch, Batcher, BatcherName
from autotransform.item.base import Item
from autotransform.item.file import FileItem
from pydantic import Field


class FileRegexBatcher(Batcher):
    """A Batcher which uses matches from regex on file content to group Items.

    Attributes:
        group_by (str): The regex which produces the group by value.
        metadata_keys (optional, Dict[str, str]): A mapping from key to a regex that produces values
            for that key.
        name (ClassVar[BatcherName]): The name of the Component.
    """

    group_by: str
    metadata_keys: Dict[str, str] = Field(default_factory=dict)

    name: ClassVar[BatcherName] = BatcherName.FILE_REGEX

    def batch(self, items: Sequence[Item]) -> List[Batch]:
        """Take filtered Items and group them by regex match values.

        Args:
            items (Sequence[Item]): The filtered Items to separate.

        Returns:
            List[Batch]: A list of Batches grouped by the extra_data of the Items.
        """

        groups: Dict[str, List[FileItem]] = defaultdict(list)
        for item in items:
            assert isinstance(item, FileItem)
            match = re.match(self.group_by, item.get_content())
            assert match is not None, "Must have value to use for grouping"
            group_by_val = match.group(1)
            groups[group_by_val].append(item)

        batches: List[Batch] = []
        for group_title, group_items in groups.items():
            batch: Batch = {"items": group_items, "title": group_title}
            if self.metadata_keys:
                metadata: Dict[str, List[Any]] = defaultdict(list)
                for item in group_items:
                    file_content = item.get_content()
                    for (
                        key,
                        regex,
                    ) in self.metadata_keys.items():  # pylint: disable=no-member
                        match = re.match(regex, file_content)
                        if match:
                            metadata[key].append(match.group(1))
                for key in metadata:
                    metadata[key] = list(set(metadata[key]))
                batch["metadata"] = metadata
            batches.append(batch)
        return batches
