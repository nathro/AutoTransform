# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""A simple factory for producing Transformers from type and param information

Note:
    Imports for custom Transformers should be in the CUSTOM IMPORTS section.
    This will reduce merge conflicts when merging in upstream changes.
    Do not auto organize imports when using custom imports to avoid merge conflicts
"""

import importlib
from typing import Any, Callable, Dict, Mapping

from autotransform.config import fetcher as Config
from autotransform.transformer.base import Transformer, TransformerBundle
from autotransform.transformer.regex import RegexTransformer
from autotransform.transformer.script import ScriptTransformer
from autotransform.transformer.type import TransformerType


class TransformerFactory:
    """The factory class

    Attributes:
        _getters (Dict[TransformerType, Callable[[Mapping[str, Any]], Transformer]]): A mapping
            from TransformerType to that transformers's from_data function.

    Note:
        Custom transformers should have their getters placed in the CUSTOM TRANSFORMERS section.
        This will reduce merge conflicts when merging in upstream changes.
    """

    # pylint: disable=too-few-public-methods

    _getters: Dict[TransformerType, Callable[[Mapping[str, Any]], Transformer]] = {
        TransformerType.REGEX: RegexTransformer.from_data,
        TransformerType.SCRIPT: ScriptTransformer.from_data,
    }

    @staticmethod
    def get(bundle: TransformerBundle) -> Transformer:
        """Simple get method using the _getters attribute

        Args:
            bundle (TransformerBundle): The decoded bundle from which to produce a Transformer
                instance

        Returns:
            Transformer: The Transformer instance of the decoded bundle
        """
        if bundle["type"] in TransformerFactory._getters:
            return TransformerFactory._getters[bundle["type"]](bundle["params"])

        custom_component_modules = Config.get_component_imports()
        for module_string in custom_component_modules:
            module = importlib.import_module(module_string)
            if hasattr(module, "TRANSFORMERS") and bundle["type"] in module.TRANSFORMERS:
                return module.TRANSFORMERS[bundle["type"]](bundle["params"])
        raise ValueError(f"No transformer found for type {bundle['type']}")
