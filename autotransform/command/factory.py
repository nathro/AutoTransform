# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from typing import Any, Callable, Dict, Mapping

from autotransform.command.base import Command, CommandBundle
from autotransform.command.type import CommandType

# Section reserved for custom imports to reduce merge conflicts
# BEGIN CUSTOM IMPORTS
# END CUSTOM IMPORTS


class CommandFactory:
    # pylint: disable=too-few-public-methods

    _getters: Dict[CommandType, Callable[[Mapping[str, Any]], Command]] = {
        # Section reserved for custom getters to reduce merge conflicts
        # BEGIN CUSTOM GETTERS
        # END CUSTOM GETTERS
    }

    @staticmethod
    def get(bundle: CommandBundle) -> Command:
        return CommandFactory._getters[bundle["type"]](bundle["params"])
