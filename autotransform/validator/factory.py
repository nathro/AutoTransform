# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from typing import Any, Callable, Dict, Mapping

from autotransform.validator.base import Validator, ValidatorBundle
from autotransform.validator.type import ValidatorType


class ValidatorFactory:
    # pylint: disable=too-few-public-methods

    _getters: Dict[ValidatorType, Callable[[Mapping[str, Any]], Validator]] = {}

    @staticmethod
    def get(validator: ValidatorBundle) -> Validator:
        return ValidatorFactory._getters[validator["type"]](validator["params"])
