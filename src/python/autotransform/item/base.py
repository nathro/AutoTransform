# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Item components. Can be used as a generic Item."""

from __future__ import annotations

from enum import Enum
from typing import Any, ClassVar, Dict, Optional

from autotransform.util.component import ComponentFactory, ComponentImport, NamedComponent


class ItemName(str, Enum):
    """A simple enum for mapping."""

    FILE = "file"
    GENERIC = "generic"


class Item(NamedComponent):
    """The base for Item components. Returned by Input components and act as the units on which
    AutoTransform operates.

    Attributes:
        key (str): A unique key used to represent this item, such as a file path.
        extra_data (Optional[Dict[str, Any]], optional): Any extra data that needs to be
            associated with this Item. Should be JSON encodable. Defaults to None.
        name (ClassVar[ItemName]): The name of the component.
    """

    key: str
    extra_data: Optional[Dict[str, Any]] = None

    name: ClassVar[ItemName] = ItemName.GENERIC


FACTORY = ComponentFactory(
    {
        ItemName.FILE: ComponentImport(class_name="FileItem", module="autotransform.item.file"),
        ItemName.GENERIC: ComponentImport(class_name="Item", module="autotransform.item.base"),
    },
    Item,  # type: ignore [misc]
    "item.json",
)
