# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Provides utility methods for interacting with the Schema map."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Optional, Sequence, Tuple

from autotransform.config import get_repo_config_relative_path
from autotransform.schema.builder import FACTORY as schema_builder_factory
from autotransform.schema.schema import AutoTransformSchema
from autotransform.util.enums import SchemaType


class SchemaMap:
    """A map that can convert Schema names in to AutoTransformSchemas.

    Attributes:
        _data (Dict[str, Tuple[SchemaType, str]]): The data that backs the Schema map.
        __instance (Optional[SchemaMap]): The singleton instance of the SchemaMap.
    """

    _data: Dict[str, Tuple[SchemaType, str]]

    __instance: Optional[SchemaMap] = None

    def __init__(self):
        """A simple constructor for a singleton class"""

        assert SchemaMap.__instance is None

        map_file_path = SchemaMap.get_schema_map_path()
        if Path(map_file_path).is_file():
            with open(map_file_path, "r", encoding="UTF-8") as map_file:
                schema_map = json.loads(map_file.read())
        else:
            schema_map = {}

        self._data = {
            name: (SchemaType(schema["type"]), schema["target"])
            for name, schema in schema_map.items()
        }

    @staticmethod
    def get() -> SchemaMap:
        """Gets the singleton instance of the SchemaMap.

        Returns:
            SchemaMap: The singleton instance of the SchemaMap.
        """

        if SchemaMap.__instance is None:
            SchemaMap.__instance = SchemaMap()

        return SchemaMap.__instance

    @staticmethod
    def get_schema_directory() -> str:
        """Gets the directory where schemas and the schema map are located.

        Returns:
            str: The directory where schemas and the schema map are located.
        """

        return os.getenv(
            "AUTO_TRANSFORM_SCHEMA_DIRECTORY",
            f"{get_repo_config_relative_path()}/schemas",
        )

    @staticmethod
    def get_schema_map_path() -> str:
        """Gets the path to the schema map.

        Returns:
            str: The path to the schema map.
        """

        return f"{SchemaMap.get_schema_directory()}/schema_map.json"

    @staticmethod
    def get_schema_path(file_name: str) -> str:
        """Gets the path to a given schema

        Args:
            file_name (str): The name of the file for a schema.

        Returns:
            str: The path where a schema is located.
        """

        return f"{SchemaMap.get_schema_directory()}/{file_name}"

    def get_schema(self, schema_name: str) -> AutoTransformSchema:
        """Get an AutoTransformSchema from the map.

        Args:
            schema_name (str): The name of the schema to get.

        Returns:
            AutoTransformSchema: The AutoTransformSchema with the supplied name.
        """

        schema_type, target = self._data[schema_name]

        if schema_type == SchemaType.BUILDER:
            return schema_builder_factory.get_instance({"name": target}).build()

        with open(SchemaMap.get_schema_path(target), "r", encoding="UTF-8") as schema_file:
            return AutoTransformSchema.from_data(json.loads(schema_file.read()))

    def add_schema(self, schema_name: str, schema_type: SchemaType, target: str) -> None:
        """Adds the specified Schema to the map.

        Args:
            schema_name (str): The name of the Schema to add.
            schema_type (SchemaType): The type of the Schema.
            target (str): The target for the Schema.
        """

        self._data[schema_name] = (schema_type, target)

    def remove_schema(self, schema_name: str) -> None:
        """Removes the specified Schema from the map.

        Args:
            schema_name (str): The name of the Schema to remove.
        """

        del self._data[schema_name]

    def write(self) -> None:
        """Writes the SchemaMap to a file as JSON."""

        schema_map_data = {
            name: {"type": schema[0], "target": schema[1]} for name, schema in self._data.items()
        }

        file_path = SchemaMap.get_schema_map_path()
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w+", encoding="UTF-8") as schema_map_file:
            schema_map_file.write(json.dumps(schema_map_data, indent=4))
            schema_map_file.flush()

    def items(self) -> Sequence[Tuple[str, Tuple[SchemaType, str]]]:
        """Gets the items in the SchemaMap.

        Returns:
            Tuple[str, Tuple[SchemaType, str]]: The items from the SchemaMap.
        """

        return list(self._data.items())

    def __contains__(self, schema_name: str) -> bool:
        """Override the contains method for the map.

        Args:
            schema_name (str): The name to check for in the SchemaMap.

        Returns:
            bool: Whether a Schema with the given name is in the map.
        """

        return schema_name in self._data

    def __getitem__(self, schema_name: str) -> AutoTransformSchema:
        """Override the subscript operator.

        Args:
            schema_name (str): The name of the Schema to get.

        Returns:
            AutoTransformSchema: The Schema with the specified name.
        """

        return self.get_schema(schema_name)
