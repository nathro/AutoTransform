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

# Section reserved for custom imports to reduce merge conflicts
# BEGIN CUSTOM IMPORTS
# END CUSTOM IMPORTS


class TransformerFactory:
    # pylint: disable=too-few-public-methods

    _getters: Dict[TransformerType, Callable[[Mapping[str, Any]], Transformer]] = {
        TransformerType.REGEX: RegexTransformer.from_data,
        # Section reserved for custom getters to reduce merge conflicts
        # BEGIN CUSTOM GETTERS
        # END CUSTOM GETTERS
    }

    @staticmethod
    def get(transformer: TransformerBundle) -> Transformer:
        return TransformerFactory._getters[transformer["type"]](transformer["params"])
