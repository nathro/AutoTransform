# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import json
import pytest
from unittest.mock import patch, MagicMock
from autotransform.filter.script import ScriptFilter
from autotransform.item.base import Item
from autotransform.filter.base import FilterName


class TestScriptFilter:
    """Test cases for the ScriptFilter class."""

    @pytest.fixture
    def script_filter(self):
        """Fixture for creating a ScriptFilter instance."""
        return ScriptFilter(args=["arg1", "arg2"], script="test_script", timeout=10)

    def test_initialization(self, script_filter):
        """Test that the ScriptFilter class correctly initializes with the provided arguments."""
        assert script_filter.args == ["arg1", "arg2"]
        assert script_filter.script == "test_script"
        assert script_filter.timeout == 10
        assert script_filter.name == FilterName.SCRIPT

    @patch("autotransform.filter.script.replace_script_args")
    @patch("autotransform.filter.script.subprocess.run")
    @patch("autotransform.filter.script.json.dump")
    @patch("autotransform.filter.script.TmpFile")
    def test_get_valid_keys(
        self,
        mock_tmp_file,
        mock_json_dump,
        mock_subprocess_run,
        mock_replace_script_args,
        script_filter,
    ):
        """Test that the _get_valid_keys method correctly runs the script and returns valid keys."""
        # Mock the temporary files
        mock_tmp_file.return_value.__enter__.return_value.name = "tmp_file"

        # Mock the subprocess.run method
        mock_subprocess_run.return_value.stdout = json.dumps(["key1", "key2"])
        mock_subprocess_run.return_value.stderr = ""
        mock_subprocess_run.return_value.returncode = 0

        # Mock the replace_script_args method
        mock_replace_script_args.return_value = ["test_script", "arg1", "arg2"]

        # Create a list of mock items
        items = [MagicMock(spec=Item) for _ in range(10)]
        for item in items:
            item.bundle.return_value = {"key": "value"}

        # Call the _get_valid_keys method
        valid_keys = script_filter._get_valid_keys(items)

        # Assert that the correct methods were called
        mock_tmp_file.assert_called()
        mock_json_dump.assert_called()
        mock_subprocess_run.assert_called()
        mock_replace_script_args.assert_called()

        # Assert that the correct keys were returned
        assert valid_keys == {"key1", "key2"}
