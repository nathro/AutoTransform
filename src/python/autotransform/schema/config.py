# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A set of configuration options for a schema."""

from __future__ import annotations

from typing import List, Optional, Type

from pydantic import Field, validator

from autotransform.util.component import ComponentModel
from autotransform.util.console import (
    choose_option,
    choose_options_from_list,
    choose_yes_or_no,
    get_str,
    input_int,
)
from autotransform.validator.base import ValidationResultLevel


class SchemaConfig(ComponentModel):  # pylint: disable=too-few-public-methods
    """An object containing all configuration information for a Schema.

    Attributes:
        schema_name (str): The unique name of the schema.
        allowed_validation_level (ValidationResultLevel, optional): The allowed level of
            validation issues. Any issues raised above this level will trigger exceptions.
            Defaults to ValidationResultLevel.NONE.
        max_submissions (Optional[int], optional): The maximum number of submissions the schema can
            create per run. If None, there is no limit. Defaults to None.
        owners (List[str], optional): The owners for the schema. Defaults to [].
    """

    schema_name: str
    allowed_validation_level: ValidationResultLevel = ValidationResultLevel.NONE
    max_submissions: Optional[int] = None
    owners: List[str] = Field(default_factory=list)

    # pylint: disable=invalid-name
    @validator("max_submissions")
    @classmethod
    def max_submissions_is_positive(cls: Type[SchemaConfig], v: Optional[int]) -> Optional[int]:
        """Validates that max submissions is positive.

        Args:
            cls (Type[SchemaConfig]): The Config class.
            v (int): The maximum number of submissions.

        Raises:
            ValueError: Raised if the maximum number of submissions is not positive.

        Returns:
            Optional[int]: The unmodified maximum number of submissions.
        """

        if v is not None and v < 1:
            raise ValueError(f"Maximum number of submissions must be positive, {v} provided")
        return v

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

        if prev_config is not None and choose_yes_or_no(
            f"Use previous maximum submissions ({prev_config.max_submissions})?"
        ):
            max_submissions = prev_config.max_submissions
        elif choose_yes_or_no("Would you like to limit the maximum number of submissions?"):
            max_submissions = input_int("Enter the maximum number of submissions", min_val=1)
        else:
            max_submissions = None

        return SchemaConfig(
            schema_name=schema_name,
            allowed_validation_level=allowed_validation_level,
            owners=list(set(owners)),
            max_submissions=max_submissions,
        )
