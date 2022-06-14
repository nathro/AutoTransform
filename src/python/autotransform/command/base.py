# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Command components."""

from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import Any, ClassVar, Mapping, Optional

from autotransform.batcher.base import Batch
from autotransform.util.component import ComponentFactory, ComponentImport, NamedComponent


class CommandName(str, Enum):
    """A simple enum for mapping."""

    SCRIPT = "script"


class Command(NamedComponent):
    """The base for Command components. Used by AutoTransform to perform post-processing
    operations after validation, such as code generation.

    Attributes:
        run_pre_validation (bool, optional): Whether to run the command before validation.
            Defaults to False.
        name (ClassVar[CommandName]): The name of the Component.
    """

    run_pre_validation: bool = False

    name: ClassVar[CommandName]

    @abstractmethod
    def run(self, batch: Batch, transform_data: Optional[Mapping[str, Any]]) -> None:
        """Performs the post-processing steps represented by the Command.

        Args:
            batch (Batch): The Batch for which this Command is run.
            transform_data (Optional[Mapping[str, Any]]): Data from the transformation.
        """


FACTORY = ComponentFactory(
    {
        CommandName.SCRIPT: ComponentImport(
            class_name="ScriptCommand", module="autotransform.command.script"
        ),
    },
    Command,  # type: ignore [misc]
    "command.json",
)
