# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""A simple factory for producing Validators from type and param information

Note:
    Imports for custom Validators should be in the CUSTOM IMPORTS section.
    This will reduce merge conflicts when merging in upstream changes.
    Do not auto organize imports when using custom imports to avoid merge conflicts
"""

import importlib
from typing import Any, Callable, Dict, Mapping

from autotransform.config import fetcher as Config
from autotransform.validator.base import Validator, ValidatorBundle
from autotransform.validator.type import ValidatorType


class ValidatorFactory:
    """The factory class

    Attributes:
        _getters (Dict[ValidatorType, Callable[[Mapping[str, Any]], Validator]]): A mapping
            from ValidatorType to that validators's from_data function.

    Note:
        Custom validators should have their getters placed in the CUSTOM VALIDATORS section.
        This will reduce merge conflicts when merging in upstream changes.
    """

    # pylint: disable=too-few-public-methods

    _getters: Dict[ValidatorType, Callable[[Mapping[str, Any]], Validator]] = {}

    @staticmethod
    def get(bundle: ValidatorBundle) -> Validator:
        """Simple get method using the _getters attribute

        Args:
            bundle (ValidatorBundle): The decoded bundle from which to produce a Validator instance

        Returns:
            Validator: The Validator instance of the decoded bundle
        """
        if bundle["type"] in ValidatorFactory._getters:
            return ValidatorFactory._getters[bundle["type"]](bundle["params"])

        custom_component_modules = Config.get_custom_component_imports()
        for module_string in custom_component_modules:
            module = importlib.import_module(module_string)
            if hasattr(module, "VALIDATORS") and bundle["type"] in module.VALIDATORS:
                return module.VALIDATORS[bundle["type"]](bundle["params"])
        raise ValueError(f"No validator found for type {bundle['type']}")
