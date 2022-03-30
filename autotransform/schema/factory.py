# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""A simple factory for producing SchemaBuilders from their name

Note:
    Imports for custom SchemaBuilders should be in the CUSTOM IMPORTS section.
    This will reduce merge conflicts when merging in upstream changes.
    Do not auto organize imports when using custom imports to avoid merge conflicts
"""

import importlib
from typing import Dict, Type

from autotransform.config import fetcher as Config
from autotransform.schema.builder import SchemaBuilder
from autotransform.schema.name import SchemaBuilderName


class SchemaBuilderFactory:
    """The factory class

    Attributes:
        _map (Dict[SchemaBuilderName, Type[SchemaBuilder]]): A mapping from SchemaBuilderName to
            the associated class

    Note:
        Custom builders should have their getters placed in the CUSTOM BUILDERS section.
        This will reduce merge conflicts when merging in upstream changes.
    """

    # pylint: disable=too-few-public-methods

    _map: Dict[SchemaBuilderName, Type[SchemaBuilder]] = {}

    @staticmethod
    def get(name: SchemaBuilderName) -> SchemaBuilder:
        """Simple get method using the _map attribute

        Args:
            name (SchemaBuilderName): The name of a SchemaBuilder

        Returns:
            SchemaBuilder: An instance of the associated SchemaBuilder
        """
        if name in SchemaBuilderFactory._map:
            return SchemaBuilderFactory._map[name]()

        custom_component_modules = Config.get_custom_component_imports()
        for module_string in custom_component_modules:
            module = importlib.import_module(module_string)
            if hasattr(module, "SCHEMAS") and name in module.SCHEMAS:
                return module.SCHEMAS[name]()
        raise ValueError(f"No schema builder found for type {name}")
