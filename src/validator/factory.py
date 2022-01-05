from typing import Any, Callable, Dict

from validator.base import Validator, ValidatorBundle
from validator.type import ValidatorType

class ValidatorFactory:
    _getters: Dict[ValidatorType, Callable[[Dict[str, Any]], Validator]] = {
    }
    
    @staticmethod
    def get(validator: ValidatorBundle) -> Validator:
        return ValidatorFactory._getters[validator["type"]](validator["params"])