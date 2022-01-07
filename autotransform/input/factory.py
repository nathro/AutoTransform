# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""A simple factory for producing Inputs from type and param information

Note:
    Imports for custom Inputs should be in the CUSTOM IMPORTS section.
    This will reduce merge conflicts when merging in upstream changes.
    Do not auto organize imports when using custom imports to avoid merge conflicts
"""

from typing import Any, Callable, Dict, Mapping

from autotransform.input.base import Input, InputBundle
from autotransform.input.directory import DirectoryInput
from autotransform.input.type import InputType

# BEGIN CUSTOM IMPORTS
# END CUSTOM IMPORTS


class InputFactory:
    """The factory class

    Attributes:
        _getters (Dict[InputType, Callable[[Mapping[str, Any]], Input]]): A mapping
            from InputType to that inputs's from_data function.

    Note:
        Custom inputs should have their getters placed in the CUSTOM INPUTS section.
        This will reduce merge conflicts when merging in upstream changes.
    """

    # pylint: disable=too-few-public-methods

    _getters: Dict[InputType, Callable[[Mapping[str, Any]], Input]] = {
        InputType.DIRECTORY: DirectoryInput.from_data,
        # BEGIN CUSTOM INPUTS
        # END CUSTOM INPUTS
    }

    @staticmethod
    def get(bundle: InputBundle) -> Input:
        """Simple get method using the _getters attribute

        Args:
            bundle (InputBundle): The decoded bundle from which to produce a Input instance

        Returns:
            Input: The Input instance of the decoded bundle
        """
        return InputFactory._getters[bundle["type"]](bundle["params"])
