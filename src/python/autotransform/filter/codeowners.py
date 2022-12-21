# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the CodeownersFilter."""

from __future__ import annotations

from functools import cached_property
from typing import ClassVar, Optional

from autotransform.filter.base import Filter, FilterName
from autotransform.item.base import Item
from autotransform.item.file import FileItem
from codeowners import CodeOwners


class CodeownersFilter(Filter):
    """A filter which uses Github CODEOWNERS files to separate changes by owner. Titles will
    be of the form 'prefix <owner>'

    Attributes:
        codeowners_location (str): The location of the CODEOWNERS file.
        owner (Optional[str]): The owner to allow files for. If None is provided, checks
            for unowned.
        name (ClassVar[FilterName]): The name of the Component.
    """

    codeowners_location: str
    owner: Optional[str]

    name: ClassVar[FilterName] = FilterName.CODEOWNERS

    @cached_property
    def _owners(self) -> CodeOwners:
        """Gets the parsed CodeOwners as a cached property.

        Returns:
            CodeOwners: The parsed CodeOwners.
        """

        with open(self.codeowners_location, mode="r", encoding="UTF-8") as codeowners_file:
            return CodeOwners(codeowners_file.read())

    @cached_property
    def _formated_owner(self) -> Optional[str]:
        if self.owner is None:
            return None
        return self.owner.removeprefix("@")

    def _is_valid(self, item: Item) -> bool:
        """Checks whether the Item is a file owned by the supplied owner. If no owner
        is supplied, checks for whether the file is unowned.

        Args:
            item (Item): The Item the Filter is checking.

        Returns:
            bool: Whether the Item passes the Filter.
        """

        if not isinstance(item, FileItem):
            return False
        owners = self._owners.of(item.get_path())

        if self.owner is None and not owners:
            return True

        if self.owner is None:
            return False

        for owner in owners:
            if self._formated_owner == owner[1].removeprefix("@"):
                return True

        return False
