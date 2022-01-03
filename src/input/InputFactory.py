from typing import Any, Dict

from input.DirectoryInput import DirectoryInput
from input.Input import Input
from input.InputType import InputType

class InputFactory:
    _getters = {
        InputType.DIRECTORY: DirectoryInput.fromData
    }
    
    @staticmethod
    def get(type: InputType, data: Dict[str, Any]) -> Input:
        return InputFactory._getters[type](data)