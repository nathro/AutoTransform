# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A script to perform a migration of a Manager JSON file from 1.0.3 to 1.0.5."""

import json
from argparse import ArgumentParser
from typing import Any, Dict, List

from autotransform.config import get_repo_config_relative_path
from autotransform.step.condition.base import ConditionName
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
    """Migrate the Manager for 1.0.3 -> 1.0.5."""

    parser = get_arg_parser()
    args = parser.parse_args()
    file_path = args.path
    if file_path is None:
        file_path = f"{get_repo_config_relative_path()}/manager.json"

    with open(file_path, "r", encoding="UTF-8") as manager_file:
        manager_json = manager_file.read()

    manager_data = json.loads(manager_json)
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
        update_condition_data(step_data["condition"])


def update_condition_data(condition_data: Dict[str, Any]) -> None:
    """Updates the Condition data to the new format.

    Args:
        condition_data (Dict[str, Any]): The Condition data to update.
    """

    if condition_data["name"] != ConditionName.CHANGE_STATE:
        return

    if isinstance(condition_data["value"], str) and condition_data["value"] in [
        "approved",
        "changes_requested",
    ]:
        condition_data["name"] = ConditionName.REVIEW_STATE
        return

    if isinstance(condition_data["value"], List):
        print("Can not migrate in/not_in comparisons for conditions")


if __name__ == "__main__":
    main()
