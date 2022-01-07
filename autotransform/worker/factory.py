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

from typing import Dict, Type

from autotransform.worker.base import Worker
from autotransform.worker.local import LocalWorker
from autotransform.worker.type import WorkerType

# BEGIN CUSTOM IMPORTS
# END CUSTOM IMPORTS


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
        return WorkerFactory._map[worker_type]
