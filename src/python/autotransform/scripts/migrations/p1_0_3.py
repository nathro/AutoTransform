# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A script to perform a migration of a Manager JSON file from 1.0.0 to 1.0.1."""

import json
import os
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Dict

from autotransform.config import get_repo_config_relative_path
from autotransform.schema.builder import FACTORY as schema_builder_factory
from autotransform.schema.schema import AutoTransformSchema
from autotransform.util.enums import SchemaType
from autotransform.util.scheduler import Scheduler


def get_arg_parser() -> ArgumentParser:
    """Gets the argument parser for migrating the Scheduler JSON file.

    Returns:
        ArgumentParser: The arg parser with all args set up.
    """

    parser = ArgumentParser(
        description="Upgrade Scheduler JSON files for 1.0.2 -> 1.0.3",
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


def main() -> None:
    """Migrate Scheduler and Schema map for 1.0.2 -> 1.0.3."""

    parser = get_arg_parser()
    args = parser.parse_args()

    # Get existing Scheduler data
    file_path = args.path
    if file_path is None:
        file_path = f"{get_repo_config_relative_path()}/scheduler.json"

    with open(file_path, "r", encoding="UTF-8") as scheduler_file:
        scheduler_json = scheduler_file.read()

    scheduler_data = json.loads(scheduler_json)

    # Get Schema Map if it exists
    map_file_path = f"{get_repo_config_relative_path()}/schema_map.json"
    if Path(map_file_path).is_file():
        with open(map_file_path, "r", encoding="UTF-8") as map_file:
            schema_map = json.loads(map_file.read())
    else:
        schema_map = {}

    update_scheduler_data(scheduler_data, schema_map)

    scheduler = Scheduler.from_data(scheduler_data)
    scheduler.write(file_path)
    os.makedirs(os.path.dirname(map_file_path), exist_ok=True)
    with open(map_file_path, "w+", encoding="UTF-8") as map_file:
        map_file.write(json.dumps(schema_map, indent=4))
        map_file.flush()


def update_scheduler_data(scheduler_data: Dict[str, Any], schema_map: Dict[str, Any]) -> None:
    """Updates Scheduler data and the Schema map for 1.0.2 -> 1.0.3 conversion.

    Args:
        scheduler_data (Dict[str, Any]): The existing Scheduler data.
        schema_map (Dict[str, Any]): The existing Schema map.
    """

    for schema_data in scheduler_data["schemas"]:
        schema_type = schema_data.get("type")

        # If type isn't present, it was already converted
        if schema_type is None:
            continue
        schema_type = SchemaType(schema_type)
        schema_target = schema_data["target"]
        if schema_type == SchemaType.BUILDER:
            schema = schema_builder_factory.get_instance({"name": schema_target}).build()
        else:
            with open(schema_target, "r", encoding="UTF-8") as schema_file:
                schema = AutoTransformSchema.from_data(json.loads(schema_file.read()))
        schema_name = schema.config.schema_name
        del schema_data["target"]
        del schema_data["type"]
        schema_data["schema_name"] = schema_name
        if schema_name in schema_map:
            assert schema_map[schema_name]["target"] == schema_target
            assert SchemaType(schema_map[schema_name]["type"]) == schema_type
        else:
            schema_map[schema_name] = {"type": schema_type, "target": schema_target}


if __name__ == "__main__":
    main()
