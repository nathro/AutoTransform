# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A set of configuration options for a schema."""

from __future__ import annotations

from typing import List, Optional

from pydantic import Field

from autotransform.util.component import ComponentModel
from autotransform.util.console import (
    choose_option,
    choose_options_from_list,
    choose_yes_or_no,
    get_str,
)
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

    @staticmethod
    def from_console(prev_config: Optional[SchemaConfig] = None) -> SchemaConfig:
        """Gets a SchemaConfig using console inputs.

        Args:
            prev_config (Optional[SchemaConfig], optional): A previously input SchemaConfig.
                Defaults to None.

        Returns:
            SchemaConfig: The input SchemaConfig.
        """

        if prev_config is not None and choose_yes_or_no(
            f"Use previous schema name ({prev_config.schema_name})?"
        ):
            schema_name = prev_config.schema_name
        else:
            schema_name = get_str("Enter the name of the schema: ")

        if prev_config is not None and choose_yes_or_no(
            f"Use previous allowed validation level ({prev_config.allowed_validation_level.value})?"
        ):
            allowed_validation_level = prev_config.allowed_validation_level
        elif choose_yes_or_no(
            f"Use default allowed validation level ({ValidationResultLevel.NONE})?"
        ):
            allowed_validation_level = ValidationResultLevel.NONE
        else:
            allowed_validation_level = choose_option(
                "Enter allowed validation level",
                [(level, [level.value.lower()]) for level in ValidationResultLevel],
            )

        if prev_config is not None and prev_config.owners:
            owners = choose_options_from_list(
                "Choose owners to keep",
                [(filt, f"{filt!r}") for filt in prev_config.owners],
                min_choices=0,
                max_choices=len(prev_config.owners),
            )
        else:
            owners = []
        extra_owners = get_str("Enter any owners as a comma separated list(blank for none): ")
        owners.extend(owner.strip() for owner in extra_owners.split(","))

        return SchemaConfig(
            schema_name=schema_name,
            allowed_validation_level=allowed_validation_level,
            owners=list(set(owners)),
        )
