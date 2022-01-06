from typing import Any, Callable, Dict

from inputsource.directory import DirectoryInput
from inputsource.base import Input, InputBundle
from inputsource.type import InputType

class InputFactory:
    _getters: Dict[InputType, Callable[[Dict[str, Any]], Input]] = {
        InputType.DIRECTORY: DirectoryInput.from_data,
    }
    
    @staticmethod
    def get(inputsource: InputBundle) -> Input:
        return InputFactory._getters[inputsource["type"]](inputsource["params"])