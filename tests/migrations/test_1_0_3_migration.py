# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that Manager migration functions as expected."""

import json
import pathlib

from autotransform.scripts.migrations.p1_0_3 import update_scheduler_data


def test_migration():
    """Test that the migration works as expected."""

    parent_dir = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/")
    with open(f"{parent_dir}/data/scheduler.input.json", "r", encoding="UTF-8") as input_scheduler:
        scheduler_data = json.loads(input_scheduler.read())
    with open(
        f"{parent_dir}/data/schema_map.input.json", "r", encoding="UTF-8"
    ) as input_schema_map:
        schema_map = json.loads(input_schema_map.read())

    update_scheduler_data(scheduler_data, schema_map)

    with open(
        f"{parent_dir}/data/scheduler.output.json", "r", encoding="UTF-8"
    ) as output_scheduler:
        expected_scheduler_data = json.loads(output_scheduler.read())
    with open(
        f"{parent_dir}/data/schema_map.output.json", "r", encoding="UTF-8"
    ) as output_schema_map:
        expected_output_schema_map = json.loads(output_schema_map.read())

    assert scheduler_data == expected_scheduler_data
    assert schema_map == expected_output_schema_map
