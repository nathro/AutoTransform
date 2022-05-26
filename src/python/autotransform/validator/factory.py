# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A simple factory for producing Validators from type and param information."""

import importlib
from typing import Any, Callable, Dict, Mapping

from autotransform.config import fetcher as Config
from autotransform.validator.base import Validator, ValidatorBundle
from autotransform.validator.script import ScriptValidator
from autotransform.validator.type import ValidatorType


class ValidatorFactory:
    """The factory class for Validators. Maps a type to a Validator.

    Attributes:
        _map (Dict[ValidatorType, Callable[[Mapping[str, Any]], Validator]]): A mapping from
            ValidatorType to the from_data function of the appropriate Validator.
    """

    # pylint: disable=too-few-public-methods

    _map: Dict[ValidatorType, Callable[[Mapping[str, Any]], Validator]] = {
        ValidatorType.SCRIPT: ScriptValidator.from_data,
    }

    @staticmethod
    def get(bundle: ValidatorBundle) -> Validator:
        """Simple get method using the _map attribute.

        Args:
            bundle (ValidatorBundle): The bundled Validator type and params.

        Returns:
            Validator: An instance of the associated Validator.
        """

        if bundle["type"] in ValidatorFactory._map:
            return ValidatorFactory._map[bundle["type"]](bundle["params"])

        custom_component_modules = Config.get_imports_components()
        for module_string in custom_component_modules:
            module = importlib.import_module(module_string)
            if hasattr(module, "VALIDATORS") and bundle["type"] in module.VALIDATORS:
                return module.VALIDATORS[bundle["type"]](bundle["params"])
        raise ValueError(f"No Validator found for type {bundle['type']}")
