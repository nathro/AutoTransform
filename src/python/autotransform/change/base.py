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
from typing import TYPE_CHECKING, Any, Generic, Mapping, TypedDict, TypeVar

from autotransform.batcher.base import Batch
from autotransform.change.state import ChangeState
from autotransform.change.type import ChangeType
from autotransform.step.action import ActionType

if TYPE_CHECKING:
    from autotransform.runner.base import Runner
    from autotransform.schema.schema import AutoTransformSchema


class ChangeBundle(TypedDict):
    """A bundled version of the Change object used for JSON encoding."""

    params: Mapping[str, Any]
    type: ChangeType


TParams = TypeVar("TParams", bound=Mapping[str, Any])


class Change(Generic[TParams], ABC):
    """The base for Change components. Used by AutoTransform to manage submissions to
    code review and source control systems.

    Attributes:
        _params (TParams): The paramaters that control operation of the Change.
            Should be defined using a TypedDict in subclasses.
    """

    _params: TParams

    def __init__(self, params: TParams):
        """A simple constructor.

        Args:
            params (TParams): The paramaters used to set up the Change.
        """

        self._params = params

    def get_params(self) -> TParams:
        """Gets the paramaters used to set up the Change.

        Returns:
            TParams: The paramaters used to set up the Change.
        """

        return self._params

    @staticmethod
    @abstractmethod
    def get_type() -> ChangeType:
        """Used to map Change components 1:1 with an enum, allowing construction from JSON.

        Returns:
            ChangeType: The unique type associated with this Change.
        """

    @abstractmethod
    def get_batch(self) -> Batch:
        """Gets the Batch that was used to produce the Change.

        Returns:
            Batch: The Batch used to produce the Change.
        """

    @abstractmethod
    def get_schema(self) -> AutoTransformSchema:
        """Gets the Schema that was used to produce the Change.

        Returns:
            AutoTransformSchema: The Schema used to produce the Change.
        """

    @abstractmethod
    def get_state(self) -> ChangeState:
        """Gets the current state of the Change.

        Returns:
            ChangeState: The current state of the Change.
        """

    def get_created_timestamp(self) -> int:
        """Returns the timestamp when the Change was created.

        Returns:
            int: The timestamp in seconds when the Change was created.
        """

    def get_last_updated_timestamp(self) -> int:
        """Returns the timestamp when the Change was last updated.

        Returns:
            int: The timestamp in seconds when the Change was last updated.
        """

    def take_action(self, action_type: ActionType, runner: Runner) -> bool:
        """Tells the Change to take an action based on the results of a Step run.

        Args:
            action_type (ActionType): The action to take.
            runner (Runner): A Runner which can be used to take an action.

        Returns:
            bool: Whether the action was taken successfully.
        """

        if action_type == ActionType.NONE:
            return True

        if action_type == ActionType.MERGE:
            return self._merge()

        if action_type == ActionType.UPDATE:
            return self._update(runner)

        if action_type == ActionType.ABANDON:
            return self.abandon()

        # No known way to handle the Action, so treat it as failed
        return False

    @abstractmethod
    def _merge(self) -> bool:
        """Merges an approved change in to main.

        Returns:
            bool: Whether the merge was completed successfully.
        """

    @abstractmethod
    def abandon(self) -> bool:
        """Close out and abandon a Change, removing it from the code review
        and/or version control system.

        Returns:
            bool: Whether the abandon was completed successfully.
        """

    def _update(self, runner: Runner) -> bool:
        """Update an outstanding Change against the latest state of the codebase.

        Args:
            runner (Runner): The Runner to use to update the Change.

        Returns:
            bool: Whether the update was completed successfully.
        """

        runner.update(self)
        return True

    def bundle(self) -> ChangeBundle:
        """Generates a JSON encodable bundle.
        If a component's params are not JSON encodable this method should be overridden to provide
        an encodable version.

        Returns:
            ChangeBundle: The encodable bundle.
        """

        return {
            "params": self._params,
            "type": self.get_type(),
        }

    @staticmethod
    @abstractmethod
    def from_data(data: Mapping[str, Any]) -> Change:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            Change: An instance of the Change.
        """
