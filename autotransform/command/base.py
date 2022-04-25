# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Command components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, Mapping, TypedDict, TypeVar

from autotransform.batcher.base import Batch
from autotransform.command.type import CommandType

TParams = TypeVar("TParams", bound=Mapping[str, Any])


class CommandBundle(TypedDict):
    """A bundled version of the Command object used for JSON encoding."""

    params: Mapping[str, Any]
    type: CommandType


class Command(Generic[TParams], ABC):
    """The base for Command components. Used by AutoTransform to perform post-processing
    operations after validation, such as code generation.

    Attributes:
        _params (TParams): The paramaters that control operation of the Command.
            Should be defined using a TypedDict in subclasses
    """

    _params: TParams

    def __init__(self, params: TParams):
        """A simple constructor.

        Args:
            params (TParams): The paramaters used to set up the Command.
        """

        self._params = params

    def get_params(self) -> TParams:
        """Gets the paramaters used to set up the Command.

        Returns:
            TParams: The paramaters used to set up the Command.
        """

        return self._params

    @staticmethod
    @abstractmethod
    def get_type() -> CommandType:
        """Used to map Command components 1:1 with an enum, allowing construction from JSON.

        Returns:
            CommandType: The unique type associated with this Command.
        """

    @abstractmethod
    def run(self, batch: Batch) -> None:
        """Performs the post-processing steps represented by the Command.

        Args:
            batch (Batch): The Batch for which this Command is run.
        """

    def bundle(self) -> CommandBundle:
        """Generates a JSON encodable bundle.
        If a component's params are not JSON encodable this method should be overridden to provide
        an encodable version.

        Returns:
            CommandBundle: The encodable bundle.
        """

        return {
            "params": self._params,
            "type": self.get_type(),
        }

    @staticmethod
    @abstractmethod
    def from_data(data: Mapping[str, Any]) -> Command:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            Command: An instance of the Command.
        """
