# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""A simple factory for producing Workers from their name

Note:
    Imports for custom Workers should be in the CUSTOM IMPORTS section.
    This will reduce merge conflicts when merging in upstream changes.
    Do not auto organize imports when using custom imports to avoid merge conflicts
"""

import importlib
from typing import Dict, Type

from autotransform.config import fetcher as Config
from autotransform.worker.base import Worker
from autotransform.worker.local import LocalWorker
from autotransform.worker.type import WorkerType


class WorkerFactory:
    """The factory class

    Attributes:
        _map (Dict[WorkerType, Type[Worker]]): A mapping from WorkerType to the associated class

    Note:
        Custom workers should have their getters placed in the CUSTOM WORKERS section.
        This will reduce merge conflicts when merging in upstream changes.
    """

    # pylint: disable=too-few-public-methods

    _map: Dict[WorkerType, Type[Worker]] = {
        WorkerType.LOCAL: LocalWorker,
        # BEGIN CUSTOM WORKERS
        # END CUSTOM WORKERS
    }

    @staticmethod
    def get(worker_type: WorkerType) -> Type[Worker]:
        """Simple get method using the _map attribute

        Args:
            worker_type (WorkerType): The type of a worker

        Returns:
            Type[Worker]: The class of the worker type
        """
        if worker_type in WorkerFactory._map:
            return WorkerFactory._map[worker_type]

        custom_component_modules = Config.get_component_imports()
        for module_string in custom_component_modules:
            module = importlib.import_module(module_string)
            if hasattr(module, "WORKERS") and worker_type in module.WORKERS:
                return module.WORKERS[worker_type]
        raise ValueError(f"No worker found for type {worker_type}")
