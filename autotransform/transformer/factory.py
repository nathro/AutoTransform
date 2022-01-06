# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from typing import Any, Callable, Dict, Mapping

from autotransform.transformer.base import Transformer, TransformerBundle
from autotransform.transformer.regex import RegexTransformer
from autotransform.transformer.type import TransformerType


class TransformerFactory:
    _getters: Dict[TransformerType, Callable[[Mapping[str, Any]], Transformer]] = {
        TransformerType.REGEX: RegexTransformer.from_data,
    }

    @staticmethod
    def get(transformer: TransformerBundle) -> Transformer:
        return TransformerFactory._getters[transformer["type"]](transformer["params"])
