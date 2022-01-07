# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from __future__ import annotations

from typing import List, Optional, Sequence, Type

from autotransform.batcher.base import Batch
from autotransform.schema.schema import AutoTransformSchema
from autotransform.worker.base import Worker


class Runner:
    schema: AutoTransformSchema
    worker_type: Type[Worker]
    workers: Optional[Sequence[Worker]]

    def __init__(self, schema: AutoTransformSchema, worker_type: Type[Worker]):
        self.worker_type = worker_type
        self.schema = schema
        self.workers = None

    def _spawn_workers(self, batches: List[Batch]) -> None:
        assert self.workers is None
        workers = self.worker_type.spawn_from_batches(self.schema, batches)
        for worker in workers:
            worker.start()
        self.workers = workers

    def start(self) -> Runner:
        batches = self.schema.get_batches()
        self._spawn_workers(batches)
        return self

    def is_finished(self) -> bool:
        workers = self.workers
        assert workers is not None
        return all(worker.is_finished() for worker in workers)

    def kill(self) -> None:
        workers = self.workers
        if workers is not None:
            for worker in workers:
                worker.kill()
