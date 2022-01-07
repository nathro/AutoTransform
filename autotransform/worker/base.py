# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The base class and associated classes for Input components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Sequence

from autotransform.batcher.base import Batch
from autotransform.schema.schema import AutoTransformSchema


class Worker(ABC):
    """The base for Workers. These are used to execute a Schema"""

    @abstractmethod
    def is_finished(self) -> bool:
        """Whether the worker has fully finished all execution.

        Returns:
            bool: False if the Worker still has things to complete
        """

    @abstractmethod
    def start(self) -> None:
        """Begin execution of the Worker (i.e. spawn a process or submit a remote job)."""

    @staticmethod
    @abstractmethod
    def spawn_from_batches(schema: AutoTransformSchema, batches: List[Batch]) -> Sequence[Worker]:
        """Create worker instances for the provided Batches. These Workers should NOT be started.
        The Runner will start all Workers.

        Args:
            schema (AutoTransformSchema): The Schema these Workers are executing
            batches (List[Batch]): The Batches the Schema found

        Returns:
            Sequence[Worker]: A list of Workers
        """

    def kill(self) -> None:
        """Kill an in process Worker and free up any associated resources. Called when the Runner is
        killed or a Worker is detected as having finished.
        """
