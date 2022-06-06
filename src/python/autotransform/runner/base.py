# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Runner components."""

from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import ClassVar

from autotransform.change.base import Change
from autotransform.schema.schema import AutoTransformSchema
from autotransform.util.component import NamedComponent, ComponentFactory, ComponentImport


class RunnerName(str, Enum):
    """A simple enum for mapping."""

    GITHUB = "github"
    LOCAL = "local"


class Runner(NamedComponent):
    """The base for Runner components. Used by AutoTransform to run an AutoTransformSchema,
    either locally on the machine or on remote infrastructure.

    Attributes:
        name (ClassVar[RunnerName]): The name of the component.
    """

    name: ClassVar[RunnerName]

    @abstractmethod
    def run(self, schema: AutoTransformSchema) -> None:
        """Triggers a full run of a Schema.

        Args:
            schema (AutoTransformSchema): The schema that will be run.
        """

    @abstractmethod
    def update(self, change: Change) -> None:
        """Triggers an update of the Change.

        Args:
            change (Change): The Change to update.
        """


FACTORY = ComponentFactory(
    {
        RunnerName.GITHUB: ComponentImport(
            class_name="GithubRunner", module="autotransform.runner.github"
        ),
        RunnerName.LOCAL: ComponentImport(
            class_name="LocalRunner", module="autotransform.runner.local"
        ),
    },
    Runner,  # type: ignore [misc]
    "runner.json",
)
