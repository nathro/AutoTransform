# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""A simple factory for producing Batchers from type and param information

Note:
    Imports for custom Batchers should be in the CUSTOM IMPORTS section.
    This will reduce merge conflicts when merging in upstream changes.
    Do not auto organize imports when using custom imports to avoid merge conflicts
"""

import importlib
from typing import Any, Callable, Dict, Mapping

from autotransform.batcher.base import Batcher, BatcherBundle
from autotransform.batcher.chunk import ChunkBatcher
from autotransform.batcher.directory import DirectoryBatcher
from autotransform.batcher.single import SingleBatcher
from autotransform.batcher.type import BatcherType
from autotransform.config import fetcher as Config


class BatcherFactory:
    """The factory class

    Attributes:
        _getters (Dict[BatcherType, Callable[[Mapping[str, Any]], Batcher]]): A mapping
            from BatcherType to that batchers's from_data function.

    Note:
        Custom batchers should have their getters placed in the CUSTOM BATCHERS section.
        This will reduce merge conflicts when merging in upstream changes.
    """

    # pylint: disable=too-few-public-methods

    _getters: Dict[BatcherType, Callable[[Mapping[str, Any]], Batcher]] = {
        BatcherType.CHUNK: ChunkBatcher.from_data,
        BatcherType.DIRECTORY: DirectoryBatcher.from_data,
        BatcherType.SINGLE: SingleBatcher.from_data,
    }

    @staticmethod
    def get(bundle: BatcherBundle) -> Batcher:
        """Simple get method using the _getters attribute

        Args:
            bundle (BatcherBundle): The decoded bundle from which to produce a Batcher instance

        Returns:
            Batcher: The Batcher instance of the decoded bundle
        """
        if bundle["type"] in BatcherFactory._getters:
            return BatcherFactory._getters[bundle["type"]](bundle["params"])

        custom_component_modules = Config.get_imports_components()
        for module_string in custom_component_modules:
            module = importlib.import_module(module_string)
            if hasattr(module, "BATCHERS") and bundle["type"] in module.BATCHERS:
                return module.BATCHERS[bundle["type"]](bundle["params"])
        raise ValueError(f"No batcher found for type {bundle['type']}")
