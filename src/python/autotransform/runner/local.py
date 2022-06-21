# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the LocalRunner."""

from __future__ import annotations

from typing import ClassVar

from autotransform.change.base import Change
from autotransform.runner.base import Runner, RunnerName
from autotransform.schema.schema import AutoTransformSchema


class LocalRunner(Runner):
    """A Runner component that runs a Schema locally on the machine.

    Attributes:
        name (ClassVar[RunnerName]): The name of the component.
    """

    name: ClassVar[RunnerName] = RunnerName.LOCAL

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
