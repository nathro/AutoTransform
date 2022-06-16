# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Input components."""

from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import ClassVar, Sequence

from autotransform.item.base import Item
from autotransform.util.component import ComponentFactory, ComponentImport, NamedComponent


class InputName(str, Enum):
    """A simple enum for mapping."""

    DIRECTORY = "directory"
    EMPTY = "empty"
    GIT_GREP = "git_grep"


class Input(NamedComponent):
    """The base for Input components. Used by AutoTransform to get Items that
    represent potentially transformable units for a Schema. Usually returns files but
    any Item can be returned as long as Schema components work with it.

    Attributes:
        name (ClassVar[InputName]): The name of the component.
    """

    name: ClassVar[InputName]

    @abstractmethod
    def get_items(self) -> Sequence[Item]:
        """Get a list of Items to be used by the transformation based on the Input criteria. Usually
        returns FileItems.

        Returns:
            Sequence[Item]: The eligible Items for transformation.
        """


FACTORY = ComponentFactory(
    {
        InputName.DIRECTORY: ComponentImport(
            class_name="DirectoryInput", module="autotransform.input.directory"
        ),
        InputName.EMPTY: ComponentImport(
            class_name="EmptyInput", module="autotransform.input.empty"
        ),
        InputName.GIT_GREP: ComponentImport(
            class_name="GitGrepInput", module="autotransform.input.gitgrep"
        ),
    },
    Input,  # type: ignore [misc]
    "input.json",
)
