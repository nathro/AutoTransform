# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A simple factory for producing Changes from type and param information."""

import importlib
from typing import Any, Callable, Dict, Mapping

from autotransform.change.base import Change, ChangeBundle
from autotransform.change.github import GithubChange
from autotransform.change.type import ChangeType
from autotransform.config import fetcher as Config


class ChangeFactory:
    """The factory class for Changes. Maps a type to a Change.

    Attributes:
        _map (Dict[ChangeType, Callable[[Mapping[str, Any]], Change]]): A mapping from
            ChangeType to the from_data function of the appropriate Change.
    """

    # pylint: disable=too-few-public-methods

    _map: Dict[ChangeType, Callable[[Mapping[str, Any]], Change]] = {
        ChangeType.GITHUB: GithubChange.from_data,
    }

    @staticmethod
    def get(bundle: ChangeBundle) -> Change:
        """Simple get method using the _map attribute.

        Args:
            bundle (ChangeBundle): The bundled Change type and params.

        Returns:
            Change: An instance of the associated Change.
        """

        if bundle["type"] in ChangeFactory._map:
            return ChangeFactory._map[bundle["type"]](bundle["params"])

        custom_component_modules = Config.get_imports_components()
        for module_string in custom_component_modules:
            module = importlib.import_module(module_string)
            if hasattr(module, "CHANGES") and bundle["type"] in module.CHANGES:
                return module.CHANGES[bundle["type"]](bundle["params"])
        raise ValueError(f"No Change found for type {bundle['type']}")
