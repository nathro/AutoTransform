from typing import Any, Dict

from input.directory import DirectoryInput
from input.base import Input
from input.type import InputType

class InputFactory:
    _getters = {
        InputType.DIRECTORY: DirectoryInput.fromData
    }
    
    @staticmethod
    def get(type: InputType, data: Dict[str, Any]) -> Input:
        return InputFactory._getters[type](data)