# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Step components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, Mapping, TypedDict, TypeVar

from autotransform.change.base import Change
from autotransform.step.action import Action
from autotransform.step.type import StepType


class StepBundle(TypedDict):
    """A bundled version of the Step object used for JSON encoding."""

    params: Mapping[str, Any]
    type: StepType


TParams = TypeVar("TParams", bound=Mapping[str, Any])


class Step(Generic[TParams], ABC):
    """The base for Step components. Used by AutoTransform to manage outstanding
    Changes, determining what actions to take.

    Attributes:
        _params (TParams): The paramaters that control operation of the Step.
            Should be defined using a TypedDict in subclasses.
    """

    _params: TParams

    def __init__(self, params: TParams):
        """A simple constructor.

        Args:
            params (TParams): The paramaters used to set up the Step.
        """

        self._params = params

    def get_params(self) -> TParams:
        """Gets the paramaters used to set up the Step.

        Returns:
            TParams: The paramaters used to set up the Step.
        """

        return self._params

    @staticmethod
    @abstractmethod
    def get_type() -> StepType:
        """Used to map Step components 1:1 with an enum, allowing construction from JSON.

        Returns:
            StepType: The unique type associated with this Step.
        """

    @abstractmethod
    def get_action(self, change: Change) -> Action:
        """Checks the Change to determine what action should be taken. If no action is needed,
        an action with ActionType.NONE can be returned.

        Args:
            change (Change): The Change the Step is running against.

        Returns:
            Action: The Action the Step wants to take.
        """

    def bundle(self) -> StepBundle:
        """Generates a JSON encodable bundle.
        If a component's params are not JSON encodable this method should be overridden to provide
        an encodable version.

        Returns:
            StepBundle: The encodable bundle.
        """

        return {
            "params": self._params,
            "type": self.get_type(),
        }

    @staticmethod
    @abstractmethod
    def from_data(data: Mapping[str, Any]) -> Step:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            Step: An instance of the Step.
        """
