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

from typing import Any, Callable, Dict, Mapping

from autotransform.validator.base import Validator, ValidatorBundle
from autotransform.validator.type import ValidatorType

# BEGIN CUSTOM IMPORTS
# END CUSTOM IMPORTS


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

    _getters: Dict[ValidatorType, Callable[[Mapping[str, Any]], Validator]] = {
        # BEGIN CUSTOM VALIDATORS
        # END CUSTOM VALIDATORS
    }

    @staticmethod
    def get(validator: ValidatorBundle) -> Validator:
        """Simple get method using the _getters attribute

        Args:
            bundle (ValidatorBundle): The decoded bundle from which to produce a Validator instance

        Returns:
            Validator: The Validator instance of the decoded bundle
        """
        return ValidatorFactory._getters[validator["type"]](validator["params"])
