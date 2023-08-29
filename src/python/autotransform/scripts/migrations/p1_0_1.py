# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A script to perform a migration of a Manager JSON file from 1.0.0 to 1.0.1."""

import json
from argparse import ArgumentParser
from typing import Any, Dict

from autotransform.config import get_repo_config_relative_path
from autotransform.step.condition.base import ConditionName
from autotransform.step.condition.comparison import ComparisonType
from autotransform.util.manager import Manager


def get_arg_parser() -> ArgumentParser:
    """Gets the argument parser for migrating the Manager JSON file.

    Returns:
        ArgumentParser: The arg parser with all args set up.
    """

    parser = ArgumentParser(
        description="Upgrade Manager JSON files for 1.0.0 -> 1.0.1",
        prog="AutoTransform",
    )

    parser.add_argument(
        "--path",
        metavar="path",
        required=False,
        type=str,
        help="A file path to the JSON encoded file, only use if file is in a non-usual place.",
    )

    return parser


def main():
    """Migrate the Manager for 1.0.0 -> 1.0.1."""

    parser = get_arg_parser()
    args = parser.parse_args()
    file_path = args.path or f"{get_repo_config_relative_path()}/manager.json"

    with open(file_path, "r", encoding="UTF-8") as manager_file:
        manager_data = json.load(manager_file)

    update_manager_data(manager_data)
    manager = Manager.from_data(manager_data)
    manager.write(file_path)


def update_manager_data(manager_data: Dict[str, Any]) -> None:
    """Updates the Manager data for the new format.

    Args:
        manager_data (Dict[str, Any]): The Manager data to update
    """

    for step in manager_data["steps"]:
        update_step_data(step)


def update_step_data(step_data: Dict[str, Any]) -> None:
    """Updates the Step data to the new format.

    Args:
        step_data (Dict[str, Any]): The Step data to update.
    """

    if step_data["name"] == "conditional":
        if "actions" not in step_data:
            step_data["actions"] = [{"name": step_data.pop("action")}]
        update_condition_data(step_data["condition"])


def update_condition_data(condition_data: Dict[str, Any]) -> None:
    """Updates the Condition data to the new format.

    Args:
        condition_data (Dict[str, Any]): The Condition data to update.
    """

    if condition_data["name"] == ConditionName.AGGREGATE:
        for sub_condition in condition_data["conditions"]:
            update_condition_data(sub_condition)

    condition_value_mapping = {
        ConditionName.CHANGE_STATE: "state",
        ConditionName.CREATED_AGO: "time",
        ConditionName.SCHEMA_NAME: "schema_name",
        ConditionName.UPDATED_AGO: "time",
    }

    if condition_data["name"] in condition_value_mapping and "value" not in condition_data:
        condition_data["value"] = condition_data.pop(
            condition_value_mapping[condition_data["name"]]
        )

    update_comparison(condition_data)


def update_comparison(condition_data: Dict[str, Any]) -> None:
    """Updates the comparison value.

    Args:
        condition_data (Dict[str, Any]): The Condition data to update
    """
    comparison_mapping = {
        "eq": ComparisonType.EQUAL,
        "neq": ComparisonType.NOT_EQUAL,
        "gt": ComparisonType.GREATER_THAN,
        "gte": ComparisonType.GREATER_THAN_OR_EQUAL,
        "lt": ComparisonType.LESS_THAN,
        "lte": ComparisonType.LESS_THAN_OR_EQUAL,
    }

    if "comparison" in condition_data:
        condition_data["comparison"] = comparison_mapping.get(
            condition_data["comparison"], condition_data["comparison"]
        )


if __name__ == "__main__":
    main()
