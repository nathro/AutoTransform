# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""An object that runs a given Schema and executes the changes by spawning Workers."""

from __future__ import annotations

from typing import List, Optional, Sequence, Type

from autotransform.batcher.base import Batch
from autotransform.schema.schema import AutoTransformSchema
from autotransform.worker.base import Worker


class Runner:
    """An object to run a schema and execute changes using Workers.

    Attributes:
        schema (AutoTransformSchema): The Schema that will be run
        worker_type (Type[Worker]): The class of the Worker objects that will be used
        workers (Optional[Sequence[Worker]]): The spawned workers once the Runner has
            been started
    """

    schema: AutoTransformSchema
    worker_type: Type[Worker]
    workers: Optional[Sequence[Worker]]

    def __init__(self, schema: AutoTransformSchema, worker_type: Type[Worker]):
        """A simple constructor.

        Args:
            schema (AutoTransformSchema): The Schema to execute
            worker_type (Type[Worker]): The class of the Workers to use
        """
        self.worker_type = worker_type
        self.schema = schema
        self.workers = None

    def _spawn_workers(self, batches: List[Batch]) -> None:
        """Spawns a set of workers based on the Batches and starts them.

        Args:
            batches (List[Batch]): The Batches obtained from the Schema
        """
        assert self.workers is None
        workers = self.worker_type.spawn_from_batches(self.schema, batches)
        for worker in workers:
            worker.start()
        self.workers = workers

    def start(self) -> Runner:
        """Gets all Batches from the schema, spawns and starts the workers.

        Returns:
            Runner: The same instance of the Runner (used for chaining)
        """
        batches = self.schema.get_batches()
        self._spawn_workers(batches)
        return self

    def is_finished(self) -> bool:
        """Checks if all Workers have finished.

        Returns:
            bool: Returns True if all Workers have finished
        """
        workers = self.workers
        assert workers is not None
        return all(worker.is_finished() for worker in workers)

    def kill(self) -> None:
        """Frees up all resources associated with a run, killing active Workers in the process."""
        workers = self.workers
        if workers is not None:
            for worker in workers:
                worker.kill()
