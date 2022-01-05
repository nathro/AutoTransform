from typing import Any, Callable, Dict

from transformer.regex import RegexTransformer
from transformer.base import Transformer, TransformerBundle
from transformer.type import TransformerType

class TransformerFactory:
    _getters: Dict[TransformerType, Callable[[Dict[str, Any]], Transformer]] = {
        TransformerType.REGEX: RegexTransformer.from_data,
    }
    
    @staticmethod
    def get(transformer: TransformerBundle) -> Transformer:
        return TransformerFactory._getters[transformer["type"]](transformer["params"])