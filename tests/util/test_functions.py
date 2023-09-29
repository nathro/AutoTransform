# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import json
import os
import pytest
import subprocess
from autotransform.item.base import Item
from autotransform.util.functions import run_cmd_on_items, replace_script_args


def test_run_cmd_on_items_valid_command():
    cmd = ["echo", "<<KEY>>"]
    items = [Item(key="test", extra_data=None)]
    batch_metadata = {"batch": "test"}
    result = run_cmd_on_items(cmd, items, batch_metadata)
    assert result.returncode == 0
    assert "test" in result.stdout


def test_run_cmd_on_items_replacement_args():
    cmd = ["echo", "<<EXTRA_DATA>>"]
    items = [Item(key="test", extra_data={"extra": "data"})]
    batch_metadata = {"batch": "test"}
    result = run_cmd_on_items(cmd, items, batch_metadata)
    assert result.returncode == 0
    assert "data" in result.stdout


def test_run_cmd_on_items_timeout():
    cmd = ["sleep", "5"]
    items = [Item(key="test", extra_data=None)]
    batch_metadata = {"batch": "test"}
    with pytest.raises(subprocess.TimeoutExpired):
        run_cmd_on_items(cmd, items, batch_metadata, timeout=1)


def test_run_cmd_on_items_command_fails():
    cmd = ["ls", "/nonexistent_directory"]
    items = [Item(key="test", extra_data=None)]
    batch_metadata = {"batch": "test"}
    result = run_cmd_on_items(cmd, items, batch_metadata)
    assert result.returncode != 0


def test_run_cmd_on_items_missing_replacement():
    cmd = ["echo", "<<MISSING>>"]
    items = [Item(key="test", extra_data=None)]
    batch_metadata = {"batch": "test"}
    result = run_cmd_on_items(cmd, items, batch_metadata)
    assert result.returncode == 0
    assert "<<MISSING>>" in result.stdout


def test_run_cmd_on_items_empty_items():
    cmd = ["echo", "no_items"]
    items = []
    batch_metadata = {"batch": "test"}
    result = run_cmd_on_items(cmd, items, batch_metadata)
    assert result.returncode == 0
    assert "no_items" in result.stdout


def test_replace_script_args():
    args = ["<<KEY>>"]
    replacements = {"<<KEY>>": ["test"]}
    result = replace_script_args(args, replacements)
    assert result == ["test"]


def test_replace_script_args_missing_replacement():
    args = ["<<MISSING>>"]
    replacements = {"<<KEY>>": ["test"]}
    result = replace_script_args(args, replacements)
    assert result == ["<<MISSING>>"]


def test_replace_script_args_env_replacement():
    os.environ["AUTO_TRANSFORM_SCRIPT_REPLACEMENTS"] = json.dumps({"<<KEY>>": ["test"]})
    args = ["<<KEY>>"]
    replacements = {}
    result = replace_script_args(args, replacements)
    assert result == ["test"]


def test_replace_script_args_empty_args():
    args = []
    replacements = {"<<KEY>>": ["test"]}
    result = replace_script_args(args, replacements)
    assert not result


def test_replace_script_args_empty_replacements():
    args = ["<<KEY>>"]
    replacements = {}
    os.environ["AUTO_TRANSFORM_SCRIPT_REPLACEMENTS"] = json.dumps({})
    result = replace_script_args(args, replacements)
    assert result == ["<<KEY>>"]
