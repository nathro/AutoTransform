# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A simple factory for producing Batchers from type and param information."""

import importlib
from typing import Any, Callable, Dict, Mapping

from autotransform.batcher.base import Batcher, BatcherBundle
from autotransform.batcher.chunk import ChunkBatcher
from autotransform.batcher.directory import DirectoryBatcher
from autotransform.batcher.single import SingleBatcher
from autotransform.batcher.type import BatcherType
from autotransform.config import fetcher as Config


class BatcherFactory:
    """The factory class for Batchers. Maps a type to a Batcher.

    Attributes:
        _map (Dict[BatcherType, Callable[[Mapping[str, Any]], Batcher]]): A mapping from
            BatcherType to the from_data function of the appropriate Batcher.
    """

    # pylint: disable=too-few-public-methods

    _map: Dict[BatcherType, Callable[[Mapping[str, Any]], Batcher]] = {
        BatcherType.CHUNK: ChunkBatcher.from_data,
        BatcherType.DIRECTORY: DirectoryBatcher.from_data,
        BatcherType.SINGLE: SingleBatcher.from_data,
    }

    @staticmethod
    def get(bundle: BatcherBundle) -> Batcher:
        """Simple get method using the _map attribute.

        Args:
            bundle (BatcherBundle): The bundled Batcher type and params.

        Returns:
            Batcher: An instance of the associated Batcher.
        """

        if bundle["type"] in BatcherFactory._map:
            return BatcherFactory._map[bundle["type"]](bundle["params"])

        custom_component_modules = Config.get_imports_components()
        for module_string in custom_component_modules:
            module = importlib.import_module(module_string)
            if hasattr(module, "BATCHERS") and bundle["type"] in module.BATCHERS:
                return module.BATCHERS[bundle["type"]](bundle["params"])
        raise ValueError(f"No Batcher found for type {bundle['type']}")
