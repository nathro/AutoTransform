# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Filter components."""

from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import ClassVar, Optional, Sequence, Set

from autotransform.item.base import Item
from autotransform.util.component import ComponentFactory, ComponentImport, NamedComponent


class FilterName(str, Enum):
    """A simple enum for mapping."""

    AGGREGATE = "aggregate"
    CODEOWNERS = "codeowners"
    FILE_EXISTS = "file_exists"
    REGEX = "regex"
    REGEX_FILE_CONTENT = "regex_file_content"
    SCRIPT = "script"

    # Shard Filters
    KEY_HASH_SHARD = "key_hash_shard"


class Filter(NamedComponent):
    """The base for Filter components. Used by AutoTransform to determine if an Item from an Input
    is eligible for transformation.

    Attributes:
        inverted (bool, optional): Whether to invert the results of the filter. Defaults to False.
        name (ClassVar[FilterName]): The name of the component.
    """

    inverted: bool = False

    name: ClassVar[FilterName]

    def is_valid(self, item: Item) -> bool:
        """Check whether an Item is valid based on the Filter and handle inversion.

        Args:
            item (Item): The Item to check.

        Returns:
            bool: Returns True if the Item is eligible for transformation.
        """

        return self.inverted != self._is_valid(item)

    @abstractmethod
    def _is_valid(self, item: Item) -> bool:
        """Check whether an Item is valid based on the Filter. Does not handle inversion.

        Args:
            item (Item): The Item to check.

        Returns:
            bool: Returns True if the Item is eligible for transformation.
        """


class BulkFilter(Filter):
    """The base for BulkFilter components. Handles validation in bulk to determine valid Items.

    Attributes:
        _valid_keys (Optional[List[str]], optional): Whether to invert the results of the filter.
            Defaults to an None.
        name (ClassVar[FilterName]): The name of the component.
    """

    _valid_keys: Optional[Set[str]] = None

    @abstractmethod
    def _get_valid_keys(self, items: Sequence[Item]) -> Set[str]:
        """Gets the valid keys from the Items.

        Args:
            items (Sequence[Item]): The Items to check for valid items.

        Returns:
            Set[str]: The keys of the valid Items.
        """

    def pre_process(self, items: Sequence[Item]) -> None:
        """Sets up the _valid_keys set for the Filter.

        Args:
            items (Sequence[Item]): The Items to validate.
        """

        if self._valid_keys is None:
            self._valid_keys = self._get_valid_keys(items)

    def _is_valid(self, item: Item) -> bool:
        """Check whether an Item is valid based on the Filter. Does not handle inversion.

        Args:
            item (Item): The Item to check.

        Returns:
            bool: Returns True if the Item is eligible for transformation.
        """

        return self._valid_keys is not None and item.key in self._valid_keys


FACTORY = ComponentFactory(
    {
        FilterName.AGGREGATE: ComponentImport(
            class_name="AggregateFilter", module="autotransform.filter.aggregate"
        ),
        FilterName.CODEOWNERS: ComponentImport(
            class_name="CodeownersFilter", module="autotransform.filter.codeowners"
        ),
        FilterName.FILE_EXISTS: ComponentImport(
            class_name="FileExistsFilter", module="autotransform.filter.file"
        ),
        FilterName.REGEX: ComponentImport(
            class_name="RegexFilter", module="autotransform.filter.regex"
        ),
        FilterName.REGEX_FILE_CONTENT: ComponentImport(
            class_name="RegexFileContentFilter", module="autotransform.filter.regex"
        ),
        FilterName.SCRIPT: ComponentImport(
            class_name="ScriptFilter", module="autotransform.filter.script"
        ),
        FilterName.KEY_HASH_SHARD: ComponentImport(
            class_name="KeyHashShardFilter", module="autotransform.filter.key_hash_shard"
        ),
    },
    Filter,  # type: ignore [type-abstract]
    "filter.json",
)
