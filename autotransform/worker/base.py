# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Sequence

from autotransform.batcher.base import Batch
from autotransform.schema.schema import AutoTransformSchema


class Worker(ABC):
    @abstractmethod
    def is_finished(self) -> bool:
        pass

    @abstractmethod
    def start(self) -> None:
        pass

    @staticmethod
    @abstractmethod
    def spawn_from_batches(schema: AutoTransformSchema, batches: List[Batch]) -> Sequence[Worker]:
        pass

    def kill(self) -> None:
        pass
