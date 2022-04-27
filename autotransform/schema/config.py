# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A set of configuration options for a schema."""

from __future__ import annotations

from typing import Any, Dict

from autotransform.validator.base import ValidationResultLevel


class SchemaConfig:
    """An object containing all configuration information for a Schema.

    Attributes:
        _allowed_validation_level (ValidationResultLevel): The allowed level of
            validation issues. Any issues raised above this level will trigger
            exceptions.
        _name (str): The unique name of the schema.
    """

    _allowed_validation_level: ValidationResultLevel
    _name: str

    def __init__(
        self,
        name: str,
        allowed_validation_level: ValidationResultLevel = ValidationResultLevel.NONE,
    ):
        """A simple constructor.

        Args:
            name (str): The unique name of the schema.
            allowed_validation_level (ValidationResultLevel, optional): The allowed level of
                validation issues. Any issues raised above this level will trigger
                exceptions. Defaults to ValidationResultLevel.NONE.
        """

        self._name = name
        self._allowed_validation_level = allowed_validation_level

    def get_name(self) -> str:
        """Gets the name of the Schema.

        Returns:
            str: The name of the Schema.
        """

        return self._name

    def get_allowed_validation_level(self) -> ValidationResultLevel:
        """Gets the allowed level of validation results for the Schema.

        Returns:
            ValidationResultLevel: The allowed level of validation results for the Schema.
        """

        return self._allowed_validation_level

    def bundle(self) -> Dict[str, Any]:
        """Bundles the configuration for JSON encoding.

        Returns:
            Dict[str, Any]: The bundled configuration.
        """

        return {
            "name": self._name,
            "allowed_validation_level": self._allowed_validation_level,
        }

    @classmethod
    def from_data(cls, data: Dict[str, Any]) -> SchemaConfig:
        """Produces a Config from supplied options.

        Args:
            data (Dict[str, Any]): The options from a bundled Config.

        Returns:
            Config: The configuration represented by the provided data.
        """

        if "allowed_validation_level" in data:
            validation_level = data["allowed_validation_level"]
            if not ValidationResultLevel.has_value(validation_level):
                validation_level = ValidationResultLevel.from_name(validation_level)
            else:
                validation_level = ValidationResultLevel.from_value(validation_level)
        else:
            validation_level = ValidationResultLevel.NONE

        name = data["name"]
        assert isinstance(name, str)
        return cls(name, validation_level)
