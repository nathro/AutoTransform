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

from autotransform.scripts.migrations.manager import update_manager_data


def test_migration():
    """Test that the migration works as expected."""

    parent_dir = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/")
    with open(f"{parent_dir}/data/manager.input.json", "r", encoding="UTF-8") as input_manager:
        manager_data = json.loads(input_manager.read())

    update_manager_data(manager_data)

    with open(f"{parent_dir}/data/manager.output.json", "r", encoding="UTF-8") as output_manager:
        expected_data = json.loads(output_manager.read())

    assert manager_data == expected_data
