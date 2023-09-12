# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from unittest.mock import patch, MagicMock
from autotransform.filter.script import ScriptFilter
from autotransform.item.base import Item


class TestScriptFilter:
    """Test cases for the ScriptFilter class."""

    def setup_method(self):
        """Setup for each test case."""
        self.script_filter = ScriptFilter(args=["arg1", "arg2"], script="test_script", timeout=10)

    def test_init(self):
        """Test that the ScriptFilter class correctly initializes."""
        assert self.script_filter.args == ["arg1", "arg2"]
        assert self.script_filter.script == "test_script"
        assert self.script_filter.timeout == 10
        assert self.script_filter.chunk_size is None

    @patch("autotransform.filter.script.replace_script_args")
    @patch("autotransform.filter.script.subprocess.run")
    @patch("autotransform.filter.script.json.dump")
    @patch("autotransform.filter.script.json.loads")
    def test_get_valid_keys(
        self, mock_json_loads, mock_json_dump, mock_subprocess_run, mock_replace_script_args
    ):
        """Test that the _get_valid_keys method works correctly."""
        # Mock the replace_script_args function to return the command with replaced args
        mock_replace_script_args.return_value = ["test_script", "arg1", "arg2"]

        # Mock the subprocess.run function to return a completed process with stdout and stderr
        mock_subprocess_run.return_value = MagicMock(
            stdout='["key1", "key2"]', stderr="", returncode=0
        )

        # Mock the json.loads function to return a list of keys
        mock_json_loads.return_value = ["key1", "key2"]

        # Create a list of mock items
        items = [MagicMock(spec=Item) for _ in range(10)]

        # Call the _get_valid_keys method
        keys = self.script_filter._get_valid_keys(items)

        # Check that the correct functions were called with the correct arguments
        mock_replace_script_args.assert_called_once()
        mock_subprocess_run.assert_called_once_with(
            ["test_script", "arg1", "arg2"],
            capture_output=True,
            encoding="utf-8",
            check=False,
            timeout=10,
        )
        mock_json_dump.assert_called_once()
        mock_json_loads.assert_called_once()

        # Check that the correct keys were returned
        assert keys == {"key1", "key2"}
