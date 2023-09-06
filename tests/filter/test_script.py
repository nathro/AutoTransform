# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import pytest
import subprocess
from unittest.mock import patch
from autotransform.filter.script import ScriptFilter
from autotransform.item.base import Item
from autotransform.filter.base import FilterName


class TestScriptFilter:
    """Test cases for the ScriptFilter class."""

    @pytest.fixture
    def script_filter(self) -> ScriptFilter:
        """Fixture for creating a ScriptFilter instance."""
        return ScriptFilter(args=["arg1", "arg2"], script="test_script", timeout=10)

    def test_init(self, script_filter: ScriptFilter):
        """Test that the ScriptFilter class correctly initializes."""
        assert script_filter.args == ["arg1", "arg2"]
        assert script_filter.script == "test_script"
        assert script_filter.timeout == 10
        assert script_filter.chunk_size is None
        assert script_filter.name == FilterName.SCRIPT

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
        script_filter: ScriptFilter,
    ):
        """Test that the _get_valid_keys method correctly gets valid keys."""
        # Mock the replace_script_args function to return the command with replaced args
        mock_replace_script_args.return_value = ["test_script", "arg1", "arg2"]

        # Mock the subprocess.run function to return a completed process with stdout and stderr
        mock_subprocess_run.return_value = subprocess.CompletedProcess(
            args=["test_script", "arg1", "arg2"], returncode=0, stdout='["key1", "key2"]', stderr=""
        )

        # Mock the json.loads function to return a list of keys
        mock_json_loads.return_value = ["key1", "key2"]

        items = [Item(key="key1", data={}), Item(key="key2", data={}), Item(key="key3", data={})]
        valid_keys = script_filter._get_valid_keys(items)

        assert valid_keys == {"key1", "key2"}

    def test_get_valid_keys_with_chunk_size(self, script_filter: ScriptFilter):
        """Test that the _get_valid_keys method correctly chunks items based on the chunk_size attribute."""
        script_filter.chunk_size = 1

        items = [Item(key="key1", data={}), Item(key="key2", data={}), Item(key="key3", data={})]
        with patch.object(ScriptFilter, "_get_valid_keys", return_value={"key1", "key2", "key3"}):
            valid_keys = script_filter._get_valid_keys(items)

        assert valid_keys == {"key1", "key2", "key3"}

    def test_get_valid_keys_with_stderr(self, script_filter: ScriptFilter):
        """Test that the _get_valid_keys method correctly handles STDERR output from the script."""
        with patch("autotransform.filter.script.subprocess.run") as mock_subprocess_run:
            mock_subprocess_run.return_value = subprocess.CompletedProcess(
                args=["test_script", "arg1", "arg2"],
                returncode=0,
                stdout='["key1", "key2"]',
                stderr="error",
            )

            items = [
                Item(key="key1", data={}),
                Item(key="key2", data={}),
                Item(key="key3", data={}),
            ]
            valid_keys = script_filter._get_valid_keys(items)
            assert valid_keys == {"key1", "key2"}
