# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from typing import Any, Callable, Dict, Mapping

from autotransform.input.base import Input, InputBundle
from autotransform.input.directory import DirectoryInput
from autotransform.input.type import InputType


class InputFactory:
    # pylint: disable=too-few-public-methods

    _getters: Dict[InputType, Callable[[Mapping[str, Any]], Input]] = {
        InputType.DIRECTORY: DirectoryInput.from_data,
    }

    @staticmethod
    def get(bundle: InputBundle) -> Input:
        return InputFactory._getters[bundle["type"]](bundle["params"])
