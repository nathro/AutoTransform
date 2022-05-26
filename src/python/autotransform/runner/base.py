# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Runner components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, Mapping, TypedDict, TypeVar

from autotransform.change.base import Change
from autotransform.runner.type import RunnerType
from autotransform.schema.schema import AutoTransformSchema

TParams = TypeVar("TParams", bound=Mapping[str, Any])


class RunnerBundle(TypedDict):
    """A bundled version of the Runner object used for JSON encoding."""

    params: Mapping[str, Any]
    type: RunnerType


class Runner(Generic[TParams], ABC):
    """The base for Runner components. Used by AutoTransform to run an AutoTransformSchema,
    either locally on the machine or on remote infrastructure.

    Attributes:
        _params (TParams): The paramaters that control operation of the Runner.
            Should be defined using a TypedDict in subclasses.
    """

    _params: TParams

    def __init__(self, params: TParams):
        """A simple constructor.

        Args:
            params (TParams): The paramaters used to set up the Runner.
        """

        self._params = params

    @staticmethod
    @abstractmethod
    def get_type() -> RunnerType:
        """Used to map Runner components 1:1 with an enum, allowing construction from JSON.

        Returns:
            RunnerType: The unique type associated with this Runner.
        """

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

    def bundle(self) -> RunnerBundle:
        """Generates a JSON encodable bundle.
        If a component's params are not JSON encodable this method should be overridden to provide
        an encodable version.

        Returns:
            RunnerBundle: The encodable bundle.
        """

        return {
            "params": self._params,
            "type": self.get_type(),
        }

    @staticmethod
    @abstractmethod
    def from_data(data: Mapping[str, Any]) -> Runner:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            Runner: An instance of the Runner.
        """
