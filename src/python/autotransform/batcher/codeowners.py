# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the CodeownersBatcher."""

from __future__ import annotations

import math
from copy import deepcopy
from typing import Any, ClassVar, Dict, List, Optional, Sequence

from autotransform.batcher.base import Batch, Batcher, BatcherName
from autotransform.item.base import Item
from autotransform.item.file import FileItem
from codeowners import CodeOwners


class CodeownersBatcher(Batcher):
    """A batcher which uses Github CODEOWNERS files to separate changes by owner. Titles will
    be of the form 'prefix <owner>'

    Attributes:
        codeowners_location (str): The location of the CODEOWNERS file.
        prefix (str): The prefix to use for titles.
        max_batch_size (Optional[int]): The maximum size of any batch. If None, then batches will
            have no max size. Defaults to None.
        metadata (Optional[Dict[str, Any]], optional): The metadata to associate with
            Batches. Defaults to None.
        name (ClassVar[BatcherName]): The name of the Component.
    """

    codeowners_location: str
    prefix: str
    max_batch_size: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

    name: ClassVar[BatcherName] = BatcherName.CODEOWNERS

    def batch(self, items: Sequence[Item]) -> List[Batch]:
        """Take filtered Items and batch them based on CODEOWNERS.

        Args:
            items (Sequence[Item]): The filtered Items to separate.

        Returns:
            List[Batch]: A list of Batches representing all items owned by a given
                owner.
        """

        team_owners: Dict[str, List[Item]] = {}
        individual_owners: Dict[str, List[Item]] = {}
        no_owners: List[Item] = []

        with open(
            self.codeowners_location, mode="r", encoding="UTF-8"
        ) as codeowners_file:
            codeowners = CodeOwners(codeowners_file.read())

        # Build Owner Dictionaries
        for item in items:
            assert isinstance(item, FileItem)
            owner = codeowners.of(item.get_path())

            if not owner:
                no_owners.append(item)
                continue

            owner_tuple = owner[0]
            owner_name = owner_tuple[1].removeprefix("@")
            if owner_tuple[0] == "USERNAME":
                individual_owners.setdefault(owner_name, []).append(item)
            elif owner_tuple[0] == "TEAM":
                team_owners.setdefault(owner_name, []).append(item)

        batches: List[Batch] = []

        # Add batches based on team owners
        batches.extend(self._create_batches(team_owners, "team_reviewers"))
        # Add batches based on individual owners
        batches.extend(self._create_batches(individual_owners, "reviewers"))
        # Add unowned batch
        if no_owners:
            batches.extend(self._create_batches({"unowned": no_owners}))

        return batches

    def _create_batches(
        self, owners: Dict[str, List[Item]], reviewer_type: Optional[str] = None
    ) -> List[Batch]:
        batches = []
        for owner, items in owners.items():
            num_chunks = (
                math.ceil(len(items) / self.max_batch_size)
                if self.max_batch_size
                else 1
            )
            chunk_size = math.ceil(len(items) / num_chunks)
            item_chunks = [
                items[i : i + chunk_size] for i in range(0, len(items), chunk_size)
            ]
            for i, chunk_items in enumerate(item_chunks, start=1):
                title = (
                    f"[{i}/{num_chunks}]{self.prefix} {owner}"
                    if num_chunks > 1
                    else f"{self.prefix} {owner}"
                )
                batch: Batch = {"items": chunk_items, "title": title}
                if self.metadata is not None:
                    # Deepcopy metadata to ensure mutations don't apply to all Batches
                    metadata = deepcopy(self.metadata)
                    if reviewer_type:
                        metadata.setdefault(reviewer_type, []).append(owner)
                    batch["metadata"] = metadata
                batches.append(batch)
        return batches
