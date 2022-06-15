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
from typing import ClassVar

from autotransform.item.base import Item
from autotransform.util.component import ComponentFactory, ComponentImport, NamedComponent


class FilterName(str, Enum):
    """A simple enum for mapping."""

    REGEX = "regex"
    REGEX_FILE_CONTENT = "regex_file_content"

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


FACTORY = ComponentFactory(
    {
        FilterName.REGEX: ComponentImport(
            class_name="RegexFilter", module="autotransform.filter.regex"
        ),
        FilterName.REGEX_FILE_CONTENT: ComponentImport(
            class_name="RegexFileContentFilter", module="autotransform.filter.regex"
        ),
        FilterName.KEY_HASH_SHARD: ComponentImport(
            class_name="KeyHashShardFilter", module="autotransform.filter.key_hash_shard"
        ),
    },
    Filter,  # type: ignore [misc]
    "filter.json",
)
