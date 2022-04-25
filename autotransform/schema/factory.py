# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A simple factory for producing SchemaBuilders from their type."""

import importlib
from typing import Dict, Type

from autotransform.config import fetcher as Config
from autotransform.schema.builder import SchemaBuilder
from autotransform.schema.type import SchemaBuilderType


class SchemaBuilderFactory:
    """The factory class for SchemaBuilders. Maps a type to a SchemaBuilder.

    Attributes:
        _map (Dict[SchemaBuilderType, Type[SchemaBuilder]]): A mapping from SchemaBuilderType to
            the associated class.
    """

    # pylint: disable=too-few-public-methods

    _map: Dict[SchemaBuilderType, Type[SchemaBuilder]] = {}

    @staticmethod
    def get(builder_type: SchemaBuilderType) -> SchemaBuilder:
        """Simple get method using the _map attribute.

        Args:
            builder_type (SchemaBuilderType): The type of a SchemaBuilder.

        Returns:
            SchemaBuilder: An instance of the associated SchemaBuilder.
        """

        if builder_type in SchemaBuilderFactory._map:
            return SchemaBuilderFactory._map[builder_type]()

        custom_component_modules = Config.get_imports_components()
        for module_string in custom_component_modules:
            module = importlib.import_module(module_string)
            if hasattr(module, "SCHEMAS") and builder_type in module.SCHEMAS:
                return module.SCHEMAS[builder_type]()
        raise ValueError(f"No schema builder found for type {builder_type}")
