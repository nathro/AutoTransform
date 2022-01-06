# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from typing import Any, Callable, Dict, Mapping

from autotransform.command.base import Command, CommandBundle
from autotransform.command.type import CommandType


class CommandFactory:
    _getters: Dict[CommandType, Callable[[Mapping[str, Any]], Command]] = {}

    @staticmethod
    def get(bundle: CommandBundle) -> Command:
        return CommandFactory._getters[bundle["type"]](bundle["params"])
