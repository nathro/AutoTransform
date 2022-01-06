# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from typing import Any, Callable, Dict, Mapping

from autotransform.batcher.base import Batcher, BatcherBundle
from autotransform.batcher.single import SingleBatcher
from autotransform.batcher.type import BatcherType


class BatcherFactory:
    # pylint: disable=too-few-public-methods

    _getters: Dict[BatcherType, Callable[[Mapping[str, Any]], Batcher]] = {
        BatcherType.SINGLE: SingleBatcher.from_data,
    }

    @staticmethod
    def get(bundle: BatcherBundle) -> Batcher:
        return BatcherFactory._getters[bundle["type"]](bundle["params"])
