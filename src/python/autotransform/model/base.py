# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Model components."""

from abc import abstractmethod
from enum import Enum
from typing import ClassVar, Generic, Sequence, Tuple, TypeVar

from autotransform.item.file import FileItem
from autotransform.util.component import (
    ComponentFactory,
    ComponentImport,
    NamedComponent,
)
from autotransform.validator.base import ValidationResult

TResultData = TypeVar("TResultData")


class ModelName(str, Enum):
    """A simple enum for mapping."""

    OPEN_AI = "open_ai"


class Model(NamedComponent, Generic[TResultData]):
    """The base for Model components. Used by AutoTransform to interact with AI models
    such as LLMs.

    Attributes:
        name (ClassVar[ModelName]): The name of the Component.
    """

    name: ClassVar[ModelName]

    @abstractmethod
    def get_result_for_item(self, item: FileItem) -> Tuple[str, TResultData]:
        """Gets a completion for a FileItem, usually used to find new file content.

        Args:
            item (FileItem): The FileItem to get the result for.

        Returns:
            Tuple[str, TResultData]: The result for the Item along with any information needed
                for future completions with validation.
        """

    @abstractmethod
    def get_result_with_validation(
        self,
        item: FileItem,
        result_data: TResultData,
        validation_failures: Sequence[ValidationResult],
    ) -> Tuple[str, TResultData]:
        """Gets a new result based on ValidationResult issues.

        Args:
            item (FileItem): The FileItem to get the result for.
            result_data (TResultData): The previously returned result data.
            validation_failures (Sequence[ValidationResult]): The validation failures.

        Returns:
            Tuple[str, TResultData]: The result for the failures along with any information needed
                for future completions.
        """


FACTORY = ComponentFactory(
    {
        ModelName.OPEN_AI: ComponentImport(
            class_name="OpenAIModel", module="autotransform.model.openai"
        ),
    },
    Model,  # type: ignore [type-abstract]
    "model.json",
)
