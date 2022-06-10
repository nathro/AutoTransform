# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A set of configuration options for a schema."""

from __future__ import annotations

from typing import List

from pydantic import Field

from autotransform.util.component import ComponentModel
from autotransform.validator.base import ValidationResultLevel


class SchemaConfig(ComponentModel):  # pylint: disable=too-few-public-methods
    """An object containing all configuration information for a Schema.

    Attributes:
        schema_name (str): The unique name of the schema.
        allowed_validation_level (ValidationResultLevel, optional): The allowed level of
            validation issues. Any issues raised above this level will trigger exceptions.
            Defaults to ValidationResultLevel.NONE.
        owners (List[str], optional): The owners for the schema. Defaults to [].
    """

    schema_name: str
    allowed_validation_level: ValidationResultLevel = ValidationResultLevel.NONE
    owners: List[str] = Field(default_factory=list)
