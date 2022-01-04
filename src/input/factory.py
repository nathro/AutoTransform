from typing import Any, Callable, Dict

from input.directory import DirectoryInput
from input.base import Input, InputBundle
from input.type import InputType

class InputFactory:
    _getters: Dict[InputType, Callable[[Dict[str, Any]], Input]] = {
        InputType.DIRECTORY: DirectoryInput.from_data
    }
    
    @staticmethod
    def get(input: InputBundle) -> Input:
        return InputFactory._getters[input["type"]](input["params"])