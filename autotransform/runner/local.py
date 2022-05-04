# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A GithubberRunner component, which is used to trigger a workflow on Github which
runs a schema."""

from __future__ import annotations

from typing import Any, Mapping, TypedDict

from autotransform.change.base import Change
from autotransform.runner.base import Runner
from autotransform.runner.type import RunnerType
from autotransform.schema.schema import AutoTransformSchema


class LocalRunnerParams(TypedDict):
    """The params required for a LocalRunner instance."""


class LocalRunner(Runner[LocalRunnerParams]):
    """A Runner component that runs a Schema locally on the machine.

    Attributes:
        _params (LocalRunnerParams): The paramaters that control operation of the Runner.
    """

    _params: LocalRunnerParams

    @staticmethod
    def get_type() -> RunnerType:
        """Used to map Runner components 1:1 with an enum, allowing construction from JSON.

        Returns:
            RunnerType: The unique type associated with this Runner.
        """

        return RunnerType.LOCAL

    def run(self, schema: AutoTransformSchema) -> None:
        """Triggers a full run of a Schema locally.

        Args:
            schema (AutoTransformSchema): The schema that will be run.
        """

        schema.run()

    def update(self, change: Change) -> None:
        """Triggers an update of the Change.

        Args:
            change (Change): The Change to update.
        """

        schema = change.get_schema()
        batch = change.get_batch()
        schema.execute_batch(batch, change)

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> LocalRunner:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            LocalRunner: An instance of the LocalRunner.
        """

        return LocalRunner({})
