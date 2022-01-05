from typing import Any, Callable, Dict

from command.base import Command, CommandBundle
from command.type import CommandType

class CommandFactory:
    _getters: Dict[CommandType, Callable[[Dict[str, Any]], Command]] = {
    }
    
    @staticmethod
    def get(command: CommandBundle) -> Command:
        return CommandFactory._getters[command["type"]](command["params"])