# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""A simple factory for producing Inputs from type and param information

Note:
    Imports for custom Inputs should be in the CUSTOM IMPORTS section.
    This will reduce merge conflicts when merging in upstream changes.
    Do not auto organize imports when using custom imports to avoid merge conflicts
"""

import importlib
from typing import Any, Callable, Dict, Mapping

from autotransform.config import fetcher as Config
from autotransform.input.base import Input, InputBundle
from autotransform.input.directory import DirectoryInput
from autotransform.input.type import InputType


class InputFactory:
    """The factory class

    Attributes:
        _getters (Dict[InputType, Callable[[Mapping[str, Any]], Input]]): A mapping
            from InputType to that inputs's from_data function.

    Note:
        Custom inputs should have their getters placed in the CUSTOM INPUTS section.
        This will reduce merge conflicts when merging in upstream changes.
    """

    # pylint: disable=too-few-public-methods

    _getters: Dict[InputType, Callable[[Mapping[str, Any]], Input]] = {
        InputType.DIRECTORY: DirectoryInput.from_data,
    }

    @staticmethod
    def get(bundle: InputBundle) -> Input:
        """Simple get method using the _getters attribute

        Args:
            bundle (InputBundle): The decoded bundle from which to produce a Input instance

        Returns:
            Input: The Input instance of the decoded bundle
        """
        if bundle["type"] in InputFactory._getters:
            return InputFactory._getters[bundle["type"]](bundle["params"])

        custom_component_modules = Config.get_custom_component_imports()
        for module_string in custom_component_modules:
            module = importlib.import_module(module_string)
            if hasattr(module, "INPUTS") and bundle["type"] in module.INPUTS:
                return module.INPUTS[bundle["type"]](bundle["params"])
        raise ValueError(f"No input found for type {bundle['type']}")
