# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A simple factory for producing Transformers from type and param information."""

import importlib
from typing import Any, Callable, Dict, Mapping

from autotransform.config import fetcher as Config
from autotransform.transformer.base import Transformer, TransformerBundle
from autotransform.transformer.regex import RegexTransformer
from autotransform.transformer.script import ScriptTransformer
from autotransform.transformer.type import TransformerType


class TransformerFactory:
    """The factory class for Transformers. Maps a type to a Transformer.

    Attributes:
        _map (Dict[TransformerType, Callable[[Mapping[str, Any]], Transformer]]): A mapping from
            TransformerType to the from_data function of the appropriate Transformer.
    """

    # pylint: disable=too-few-public-methods

    _map: Dict[TransformerType, Callable[[Mapping[str, Any]], Transformer]] = {
        TransformerType.REGEX: RegexTransformer.from_data,
        TransformerType.SCRIPT: ScriptTransformer.from_data,
    }

    @staticmethod
    def get(bundle: TransformerBundle) -> Transformer:
        """Simple get method using the _map attribute.

        Args:
            bundle (TransformerBundle): The bundled Transformer type and params.

        Returns:
            Transformer: An instance of the associated Transformer.
        """

        if bundle["type"] in TransformerFactory._map:
            return TransformerFactory._map[bundle["type"]](bundle["params"])

        custom_component_modules = Config.get_imports_components()
        for module_string in custom_component_modules:
            module = importlib.import_module(module_string)
            if hasattr(module, "TRANSFORMERS") and bundle["type"] in module.TRANSFORMERS:
                return module.TRANSFORMERS[bundle["type"]](bundle["params"])
        raise ValueError(f"No Transformer found for type {bundle['type']}")
