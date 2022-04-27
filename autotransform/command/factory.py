# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A simple factory for producing Commands from type and param information."""

import importlib
from typing import Any, Callable, Dict, Mapping

from autotransform.command.base import Command, CommandBundle
from autotransform.command.script import ScriptCommand
from autotransform.command.type import CommandType
from autotransform.config import fetcher as Config


class CommandFactory:
    """The factory class for Commands. Maps a type to a Command.

    Attributes:
        _map (Dict[CommandType, Callable[[Mapping[str, Any]], Command]]): A mapping from
            CommandType to the from_data function of the appropriate Command.
    """

    # pylint: disable=too-few-public-methods

    _map: Dict[CommandType, Callable[[Mapping[str, Any]], Command]] = {
        CommandType.SCRIPT: ScriptCommand.from_data,
    }

    @staticmethod
    def get(bundle: CommandBundle) -> Command:
        """Simple get method using the _map attribute.

        Args:
            bundle (CommandBundle): The bundled Command type and params.

        Returns:
            Command: An instance of the associated Command.
        """

        if bundle["type"] in CommandFactory._map:
            return CommandFactory._map[bundle["type"]](bundle["params"])

        custom_component_modules = Config.get_imports_components()
        for module_string in custom_component_modules:
            module = importlib.import_module(module_string)
            if hasattr(module, "COMMANDS") and bundle["type"] in module.COMMANDS:
                return module.COMMANDS[bundle["type"]](bundle["params"])
        raise ValueError(f"No Command found for type {bundle['type']}")
