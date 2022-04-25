# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A simple factory for producing Inputs from type and param information."""

import importlib
from typing import Any, Callable, Dict, Mapping

from autotransform.config import fetcher as Config
from autotransform.input.base import Input, InputBundle
from autotransform.input.directory import DirectoryInput
from autotransform.input.gitgrep import GitGrepInput
from autotransform.input.type import InputType


class InputFactory:
    """The factory class for Inputs. Maps a type to an Input.

    Attributes:
        _map (Dict[InputType, Callable[[Mapping[str, Any]], Input]]): A mapping from
            InputType to the from_data function of the appropriate Input.
    """

    # pylint: disable=too-few-public-methods

    _map: Dict[InputType, Callable[[Mapping[str, Any]], Input]] = {
        InputType.DIRECTORY: DirectoryInput.from_data,
        InputType.GIT_GREP: GitGrepInput.from_data,
    }

    @staticmethod
    def get(bundle: InputBundle) -> Input:
        """Simple get method using the _map attribute.

        Args:
            bundle (InputBundle): The bundled Input type and params.

        Returns:
            Input: An instance of the associated Input.
        """
        if bundle["type"] in InputFactory._map:
            return InputFactory._map[bundle["type"]](bundle["params"])

        custom_component_modules = Config.get_imports_components()
        for module_string in custom_component_modules:
            module = importlib.import_module(module_string)
            if hasattr(module, "INPUTS") and bundle["type"] in module.INPUTS:
                return module.INPUTS[bundle["type"]](bundle["params"])
        raise ValueError(f"No Input found for type {bundle['type']}")
