# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the CodeownersFilter."""

from functools import cached_property
from typing import Any, ClassVar, Dict, Optional

from autotransform.filter.base import Filter, FilterName
from autotransform.item.base import Item
from autotransform.item.file import FileItem
from codeowners import CodeOwners
from pydantic import model_validator


class CodeownersFilter(Filter):
    """A filter which uses Github CODEOWNERS files to separate changes by owner. Titles will
    be of the form 'prefix <owner>'

    Attributes:
        codeowners_file_path (str): The path of the CODEOWNERS file.
        owner (Optional[str]): The owner to allow files for. If None is provided, checks
            for unowned.
        name (ClassVar[FilterName]): The name of the Component.
    """

    codeowners_file_path: str
    owner: Optional[str] = None

    name: ClassVar[FilterName] = FilterName.CODEOWNERS

    @model_validator(mode="before")
    @classmethod
    def path_legacy_setting_validator(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validates codeowners_file_path using legacy codeowners_location setting.

        Args:
            values (Dict[str, Any]): The values used to configure the CodeownersFilter.

        Raises:
            ValueError: Raised if both codeowners_file_path and codeowners_location are supplied.

        Returns:
            Mapping[str, Any]: The fixed values.
        """

        if "codeowners_location" in values:
            if (
                "codeowners_file_path" in values
                and values["codeowners_file_path"] != values["codeowners_location"]
            ):
                raise ValueError(
                    "Can not supply both codeowners_location and codeowners_file_path "
                    + "for DirectoryInput"
                )
            values["codeowners_file_path"] = values["codeowners_location"]
        return values

    @cached_property
    def _owners(self) -> CodeOwners:
        """Gets the parsed CodeOwners as a cached property.

        Returns:
            CodeOwners: The parsed CodeOwners.
        """

        with open(
            self.codeowners_file_path, mode="r", encoding="UTF-8"
        ) as codeowners_file:
            return CodeOwners(codeowners_file.read())

    @cached_property
    def _formatted_owner(self) -> Optional[str]:
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

        if self.owner is None:
            return not owners

        return any(
            self._formatted_owner == owner[1].removeprefix("@") for owner in owners
        )
