# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from typing import Dict, Type

from autotransform.worker.base import Worker
from autotransform.worker.local import LocalWorker
from autotransform.worker.type import WorkerType

# Section reserved for custom imports to reduce merge conflicts
# BEGIN CUSTOM IMPORTS
# END CUSTOM IMPORTS


class WorkerFactory:
    # pylint: disable=too-few-public-methods

    _map: Dict[WorkerType, Type[Worker]] = {
        WorkerType.LOCAL: LocalWorker,
        # Section reserved for custom workers to reduce merge conflicts
        # BEGIN CUSTOM WORKERS
        # END CUSTOM WORKERS
    }

    @staticmethod
    def get(worker_type: WorkerType) -> Type[Worker]:
        return WorkerFactory._map[worker_type]
