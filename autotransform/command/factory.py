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

from typing import Any, Callable, Dict, Mapping

from autotransform.command.base import Command, CommandBundle
from autotransform.command.type import CommandType

# BEGIN CUSTOM IMPORTS
# END CUSTOM IMPORTS


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

    _getters: Dict[CommandType, Callable[[Mapping[str, Any]], Command]] = {
        # BEGIN CUSTOM COMMANDS
        # END CUSTOM COMMANDS
    }

    @staticmethod
    def get(bundle: CommandBundle) -> Command:
        """Simple get method using the _getters attribute

        Args:
            bundle (CommandBundle): The decoded bundle from which to produce a Command instance

        Returns:
            Command: The Command instance of the decoded bundle
        """
        return CommandFactory._getters[bundle["type"]](bundle["params"])
