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
from autotransform.schema.builder import FACTORY as schema_builder_factory
from autotransform.schema.schema import AutoTransformSchema
from autotransform.util.enums import SchemaType
from autotransform.util.scheduler import Scheduler
from autotransform.util.schema_map import SchemaMap


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


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON data from a file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        Dict[str, Any]: The loaded JSON data.
    """
    with open(file_path, "r", encoding="UTF-8") as json_file:
        return json.loads(json_file.read())


def main() -> None:
    """Migrate Scheduler and Schema map for 1.0.2 -> 1.0.3."""

    parser = get_arg_parser()
    args = parser.parse_args()

    # Get existing Scheduler data
    file_path = args.path or f"{get_repo_config_relative_path()}/scheduler.json"

    scheduler_data = load_json_file(file_path)

    schema_map = SchemaMap.get()
    update_scheduler_data(scheduler_data, schema_map)

    scheduler = Scheduler.from_data(scheduler_data)
    scheduler.write(file_path)
    schema_map.write()


def update_scheduler_data(scheduler_data: Dict[str, Any], schema_map: SchemaMap) -> None:
    """Updates Scheduler data and the Schema map for 1.0.2 -> 1.0.3 conversion.

    Args:
        scheduler_data (Dict[str, Any]): The existing Scheduler data.
        schema_map (SchemaMap): The existing Schema map.
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
            schema = AutoTransformSchema.from_data(load_json_file(schema_target))
        schema_name = schema.config.schema_name
        del schema_data["target"]
        del schema_data["type"]
        schema_data["schema_name"] = schema_name
        if schema_name not in schema_map:
            schema_map.add_schema(schema_name, schema_type, schema_target)


if __name__ == "__main__":
    main()
