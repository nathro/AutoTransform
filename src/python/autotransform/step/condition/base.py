# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Change components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, Mapping, TypedDict, TypeVar

from autotransform.change.base import Change
from autotransform.step.condition.type import ConditionType


class ConditionBundle(TypedDict):
    """A bundled version of the Condition object used for JSON encoding."""

    params: Mapping[str, Any]
    type: ConditionType


TParams = TypeVar("TParams", bound=Mapping[str, Any])


class Condition(Generic[TParams], ABC):
    """The base for Condition components. Used by ConditionalStep to determine whether to
    take an Action.

    Attributes:
        _params (TParams): The paramaters that control operation of the Condition.
            Should be defined using a TypedDict in subclasses.
    """

    _params: TParams

    def __init__(self, params: TParams):
        """A simple constructor.

        Args:
            params (TParams): The paramaters used to set up the Condition.
        """

        self._params = params

    def get_params(self) -> TParams:
        """Gets the paramaters used to set up the Condition.

        Returns:
            TParams: The paramaters used to set up the Condition.
        """

        return self._params

    @staticmethod
    @abstractmethod
    def get_type() -> ConditionType:
        """Used to map Condition components 1:1 with an enum, allowing construction from JSON.

        Returns:
            ConditionType: The unique type associated with this Condition.
        """

    @abstractmethod
    def check(self, change: Change) -> bool:
        """Checks whether the Change passes the Condition.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            bool: Whether the Change passes the condition.
        """

    def bundle(self) -> ConditionBundle:
        """Generates a JSON encodable bundle.
        If a component's params are not JSON encodable this method should be overridden to provide
        an encodable version.

        Returns:
            ConditionBundle: The encodable bundle.
        """

        return {
            "params": self._params,
            "type": self.get_type(),
        }

    @staticmethod
    @abstractmethod
    def from_data(data: Mapping[str, Any]) -> Condition:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            Condition: An instance of the Condition.
        """
