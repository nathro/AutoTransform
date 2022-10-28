# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the CodeownersBatcher."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, ClassVar, Dict, List, Optional, Sequence

from codeowners import CodeOwners

from autotransform.batcher.base import Batch, Batcher, BatcherName
from autotransform.item.base import Item
from autotransform.item.file import FileItem


class CodeownersBatcher(Batcher):
    """A batcher which uses Github CODEOWNERS files to separate changes by owner. Titles will
    be of the form 'prefix <owner>'

    Attributes:
        codeowners_location (str): The location of the CODEOWNERS file.
        prefix (str): The prefix to use for titles.
        metadata (Optional[Dict[str, Any]], optional): The metadata to associate with
            Batches. Defaults to None.
        name (ClassVar[BatcherName]): The name of the Component.
    """

    codeowners_location: str
    prefix: str
    metadata: Optional[Dict[str, Any]] = None

    name: ClassVar[BatcherName] = BatcherName.CODEOWNERS

    # pylint: disable=too-many-branches
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

        with open(self.codeowners_location, mode="r", encoding="UTF-8") as codeowners_file:
            codeowners = CodeOwners(codeowners_file.read())

        # Build Owner Dictionaries
        for item in items:
            assert isinstance(item, FileItem)
            owner = codeowners.of(item.get_path())

            if not owner:
                no_owners.append(item)
                continue

            owner_tuple = owner[0]
            if owner_tuple[0] == "USERNAME":
                owner_name = owner_tuple[1]
                if owner_name not in individual_owners:
                    individual_owners[owner_name] = []
                individual_owners[owner_name].append(item)

            if owner_tuple[0] == "TEAM":
                owner_name = owner_tuple[1]
                if owner_name not in team_owners:
                    team_owners[owner_name] = []
                team_owners[owner_name].append(item)

        batches: List[Batch] = []

        # Add batches based on team owners
        for team_owner, batch_items in team_owners.items():
            batch: Batch = {"items": batch_items, "title": f"{self.prefix} {team_owner}"}
            if self.metadata is not None:
                # Deepcopy metadata to ensure mutations don't apply to all Batches
                batch["metadata"] = deepcopy(self.metadata)
            else:
                batch["metadata"] = {}
            if (
                "team_reviewers" in batch["metadata"]
                and team_owner not in batch["metadata"]["team_reviewers"]
            ):
                batch["metadata"]["team_reviewers"].append(team_owner)
            batches.append(batch)

        # Add batches based on individual owners
        for individual_owner, batch_items in individual_owners.items():
            batch = {"items": batch_items, "title": f"{self.prefix} {individual_owner}"}
            if self.metadata is not None:
                # Deepcopy metadata to ensure mutations don't apply to all Batches
                batch["metadata"] = deepcopy(self.metadata)
            else:
                batch["metadata"] = {}
            if (
                "reviewers" in batch["metadata"]
                and individual_owner not in batch["metadata"]["reviewers"]
            ):
                batch["metadata"]["reviewers"].append(individual_owner)
            batches.append(batch)

        # Add unowned batch
        batch = {"items": batch_items, "title": f"{self.prefix} unowned"}
        if self.metadata is not None:
            # Deepcopy metadata to ensure mutations don't apply to all Batches
            batch["metadata"] = deepcopy(self.metadata)

        batches.append(batch)

        return batches
