#    _____          __       ___________                              _____                     
#   /  _  \  __ ___/  |_  ___\__    ___/___________    ____   _______/ ____\___________  _____  
#  /  /_\  \|  |  \   __\/  _ \|    |  \_  __ \__  \  /    \ /  ___/\   __\/  _ \_  __ \/     \ 
# /    |    \  |  /|  | (  <_> )    |   |  | \// __ \|   |  \\___ \  |  | (  <_> )  | \/  Y Y  \
# \____|__  /____/ |__|  \____/|____|   |__|  (____  /___|  /____  > |__|  \____/|__|  |__|_|  /
#         \/                                       \/     \/     \/                          \/ 

# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

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