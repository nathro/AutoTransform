# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import pytest
import subprocess
from unittest.mock import patch, MagicMock, ANY
from autotransform.filter.script import ScriptFilter
from autotransform.item.base import Item


class TestScriptFilter:
    """Test cases for the ScriptFilter class."""

    @pytest.fixture
    def script_filter(self):
        """Fixture for creating a ScriptFilter instance."""
        return ScriptFilter(args=["arg1", "arg2"], script="test_script", timeout=10)

    def test_init(self, script_filter):
        """Test that the ScriptFilter class initializes correctly."""
        assert script_filter.args == ["arg1", "arg2"]
        assert script_filter.script == "test_script"
        assert script_filter.timeout == 10

    @patch("autotransform.filter.script.replace_script_args")
    @patch("autotransform.filter.script.subprocess.run")
    @patch("autotransform.filter.script.json.dump")
    @patch("autotransform.filter.script.json.loads")
    def test_get_valid_keys(
        self,
        mock_json_loads,
        mock_json_dump,
        mock_subprocess_run,
        mock_replace_script_args,
        script_filter,
    ):
        """Test that the _get_valid_keys method correctly gets the valid keys from the items using a script."""
        mock_item = MagicMock(spec=Item)
        mock_item.bundle.return_value = {"key": "value"}
        items = [mock_item]

        mock_json_loads.return_value = ["key"]
        mock_subprocess_run.return_value = subprocess.CompletedProcess(
            args=["test_script", "arg1", "arg2"], returncode=0, stdout='["key"]', stderr=""
        )
        mock_replace_script_args.return_value = ["test_script", "arg1", "arg2"]

        valid_keys = script_filter._get_valid_keys(items)

        assert valid_keys == set(["key"])
        mock_json_dump.assert_called_once_with([{"key": "value"}], ANY)
        mock_json_loads.assert_called_once()
        mock_subprocess_run.assert_called_once()
        mock_replace_script_args.assert_called_once()

    @patch("autotransform.filter.script.replace_script_args")
    @patch("autotransform.filter.script.subprocess.run")
    @patch("autotransform.filter.script.json.dump")
    @patch("autotransform.filter.script.json.loads")
    def test_get_valid_keys_with_result_file(
        self,
        mock_json_loads,
        mock_json_dump,
        mock_subprocess_run,
        mock_replace_script_args,
        script_filter,
    ):
        """Test that the _get_valid_keys method correctly replaces the <<RESULT_FILE>> argument with the path of a temporary file."""
        mock_item = MagicMock(spec=Item)
        mock_item.bundle.return_value = {"key": "value"}
        items = [mock_item]

        script_filter.args.append("<<RESULT_FILE>>")

        mock_json_loads.return_value = ["key"]
        mock_subprocess_run.return_value = subprocess.CompletedProcess(
            args=["test_script", "arg1", "arg2", "<<RESULT_FILE>>"],
            returncode=0,
            stdout="",
            stderr="",
        )
        mock_replace_script_args.return_value = ["test_script", "arg1", "arg2", "<<RESULT_FILE>>"]

        valid_keys = script_filter._get_valid_keys(items)

        assert valid_keys == set(["key"])
        mock_json_dump.assert_called_once_with([{"key": "value"}], ANY)
        mock_json_loads.assert_called_once()
        mock_subprocess_run.assert_called_once()
        mock_replace_script_args.assert_called_once()

    # Add more test cases as needed...
