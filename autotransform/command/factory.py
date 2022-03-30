# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""A simple factory for producing Commands from type and param information

Note:
    Imports for custom Commands should be in the CUSTOM IMPORTS section.
    This will reduce merge conflicts when merging in upstream changes.
    Do not auto organize imports when using custom imports to avoid merge conflicts
"""

import importlib
from typing import Any, Callable, Dict, Mapping

from autotransform.command.base import Command, CommandBundle
from autotransform.command.type import CommandType
from autotransform.config import fetcher as Config


class CommandFactory:
    """The factory class

    Attributes:
        _getters (Dict[CommandType, Callable[[Mapping[str, Any]], Command]]): A mapping
            from CommandType to that commands's from_data function.

    Note:
        Custom commands should have their getters placed in the CUSTOM COMMANDS section.
        This will reduce merge conflicts when merging in upstream changes.
    """

    # pylint: disable=too-few-public-methods

    _getters: Dict[CommandType, Callable[[Mapping[str, Any]], Command]] = {}

    @staticmethod
    def get(bundle: CommandBundle) -> Command:
        """Simple get method using the _getters attribute

        Args:
            bundle (CommandBundle): The decoded bundle from which to produce a Command instance

        Returns:
            Command: The Command instance of the decoded bundle
        """
        if bundle["type"] in CommandFactory._getters:
            return CommandFactory._getters[bundle["type"]](bundle["params"])

        custom_component_modules = Config.get_custom_component_imports()
        for module_string in custom_component_modules:
            module = importlib.import_module(module_string)
            if hasattr(module, "COMMANDS") and bundle["type"] in module.COMMANDS:
                return module.COMMANDS[bundle["type"]](bundle["params"])
        raise ValueError(f"No command found for type {bundle['type']}")
