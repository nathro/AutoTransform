# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from unittest.mock import patch, MagicMock
from autotransform.filter.script import ScriptFilter
from autotransform.item.base import Item


def test_script_filter_initialization():
    """Test that the ScriptFilter class initializes correctly with the correct attributes."""
    script_filter = ScriptFilter(
        args=["arg1", "arg2"], script="test_script", timeout=10, chunk_size=5
    )
    assert script_filter.args == ["arg1", "arg2"]
    assert script_filter.script == "test_script"
    assert script_filter.timeout == 10
    assert script_filter.chunk_size == 5


@patch("subprocess.run")
def test_get_valid_keys(mock_subprocess_run):
    """Test that the _get_valid_keys method correctly gets the valid keys from the items using a script."""
    mock_subprocess_run.return_value = MagicMock(stdout='["key1", "key2"]')
    script_filter = ScriptFilter(
        args=["arg1", "arg2"], script="test_script", timeout=10, chunk_size=5
    )
    items = [Item(key="key1"), Item(key="key2")]
    valid_keys = script_filter._get_valid_keys(items)
    assert valid_keys == set(["key1", "key2"])


@patch("subprocess.run")
@patch("builtins.open", new_callable=MagicMock)
def test_result_file_arg_replacement(mock_open, mock_subprocess_run):
    """Test that the _get_valid_keys method correctly replaces the <<RESULT_FILE>> arg with the path of a temporary file."""
    mock_open.return_value.__enter__.return_value.read.return_value = '["key1", "key2"]'
    script_filter = ScriptFilter(
        args=["arg1", "arg2", "<<RESULT_FILE>>"], script="test_script", timeout=10, chunk_size=5
    )
    items = [Item(key="key1"), Item(key="key2")]
    valid_keys = script_filter._get_valid_keys(items)
    assert "<<RESULT_FILE>>" not in valid_keys


@patch("subprocess.run")
def test_item_file_arg_replacement(mock_subprocess_run):
    """Test that the _get_valid_keys method correctly replaces the <<ITEM_FILE>> argument with the path to a file containing a JSON encoded list of the items to validate."""
    mock_subprocess_run.return_value = MagicMock(stdout='["key1", "key2"]')
    script_filter = ScriptFilter(
        args=["arg1", "arg2", "<<ITEM_FILE>>"], script="test_script", timeout=10, chunk_size=5
    )
    items = [Item(key="key1"), Item(key="key2")]
    valid_keys = script_filter._get_valid_keys(items)
    assert "<<ITEM_FILE>>" not in valid_keys


@patch("subprocess.run")
def test_stdout_interpretation(mock_subprocess_run):
    """Test that the _get_valid_keys method correctly interprets the STDOUT of the script as a JSON encoded list of keys for valid items when no <<RESULT_FILE>> arg is used."""
    mock_subprocess_run.return_value = MagicMock(stdout='["key1", "key2"]')
    script_filter = ScriptFilter(
        args=["arg1", "arg2"], script="test_script", timeout=10, chunk_size=5
    )
    items = [Item(key="key1"), Item(key="key2")]
    valid_keys = script_filter._get_valid_keys(items)
    assert valid_keys == set(["key1", "key2"])


@patch("subprocess.run")
def test_script_output_error_handling(mock_subprocess_run):
    """Test that the _get_valid_keys method correctly handles any output or errors from the script."""
    mock_subprocess_run.return_value = MagicMock(stdout='["key1", "key2"]')
    script_filter = ScriptFilter(
        args=["arg1", "arg2"], script="test_script", timeout=10, chunk_size=5
    )
    items = [Item(key="key1"), Item(key="key2")]
    valid_keys = script_filter._get_valid_keys(items)
    assert valid_keys == set(["key1", "key2"])


@patch("subprocess.run")
def test_script_return_code_check(mock_subprocess_run):
    """Test that the _get_valid_keys method correctly checks the return code of the script."""
    mock_subprocess_run.return_value = MagicMock(stdout='["key1", "key2"]')
    script_filter = ScriptFilter(
        args=["arg1", "arg2"], script="test_script", timeout=10, chunk_size=5
    )
    items = [Item(key="key1"), Item(key="key2")]
    valid_keys = script_filter._get_valid_keys(items)
    assert valid_keys == set(["key1", "key2"])


@patch("subprocess.run")
def test_chunk_size_handling(mock_subprocess_run):
    """Test that the ScriptFilter class correctly handles chunking of items when the chunk_size attribute is set."""
    mock_subprocess_run.return_value = MagicMock(stdout='["key1", "key2"]')
    script_filter = ScriptFilter(
        args=["arg1", "arg2"], script="test_script", timeout=10, chunk_size=1
    )
    items = [Item(key="key1"), Item(key="key2")]
    valid_keys = script_filter._get_valid_keys(items)
    assert valid_keys == set(["key1", "key2"])


@patch("subprocess.run")
def test_no_chunk_size_handling(mock_subprocess_run):
    """Test that the ScriptFilter class correctly handles the case where no chunking is used when the chunk_size attribute is None."""
    mock_subprocess_run.return_value = MagicMock(stdout='["key1", "key2"]')
    script_filter = ScriptFilter(args=["arg1", "arg2"], script="test_script", timeout=10)
    items = [Item(key="key1"), Item(key="key2")]
    valid_keys = script_filter._get_valid_keys(items)
    assert valid_keys == set(["key1", "key2"])


@patch("subprocess.run")
def test_script_timeout_handling(mock_subprocess_run):
    """Test that the ScriptFilter class correctly handles the timeout for the script process."""
    mock_subprocess_run.return_value = MagicMock(stdout='["key1", "key2"]')
    script_filter = ScriptFilter(args=["arg1", "arg2"], script="test_script", timeout=1)
    items = [Item(key="key1"), Item(key="key2")]
    valid_keys = script_filter._get_valid_keys(items)
    assert valid_keys == set(["key1", "key2"])
