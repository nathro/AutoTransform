# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Transformer components."""

from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import Any, ClassVar, Generic, Mapping, Optional, TypeVar

from autotransform.batcher.base import Batch
from autotransform.util.component import ComponentFactory, ComponentImport, NamedComponent

TResult = TypeVar("TResult", bound=Optional[Mapping[str, Any]])


class TransformerName(str, Enum):
    """A simple enum for mapping."""

    AI_MODEL = "ai_model"
    JSCODESHIFT = "jscodeshift"
    LIBCST = "libcst"
    REGEX = "regex"
    SCRIPT = "script"


class Transformer(Generic[TResult], NamedComponent):
    """The base for Transformer components. Transformers are used to execute changes to a codebase.
    A Transformer takes in a Batch and then executes all changes associated with the Batch.

    Attributes:
        name (ClassVar[TransformerName]): The name of the component.
    """

    name: ClassVar[TransformerName]

    @abstractmethod
    def transform(self, batch: Batch) -> TResult:
        """Execute a transformation against the provided Batch. All writing should be done via
        CachedFile's write_content method or FileItem's write_content method to ensure operations
        are easily accessible to testing and file content cache's are kept accurate.

        Args:
            batch (Batch): The Batch that will be transformed.
        """


FACTORY = ComponentFactory(
    {
        TransformerName.AI_MODEL: ComponentImport(
            class_name="AIModelTransformer", module="autotransform.transformer.aimodel"
        ),
        TransformerName.JSCODESHIFT: ComponentImport(
            class_name="JSCodeshiftTransformer", module="autotransform.transformer.jscodeshift"
        ),
        TransformerName.LIBCST: ComponentImport(
            class_name="LibCSTTransformer", module="autotransform.transformer.libcst"
        ),
        TransformerName.REGEX: ComponentImport(
            class_name="RegexTransformer", module="autotransform.transformer.regex"
        ),
        TransformerName.SCRIPT: ComponentImport(
            class_name="ScriptTransformer", module="autotransform.transformer.script"
        ),
    },
    Transformer,  # type: ignore [type-abstract]
    "transformer.json",
)
