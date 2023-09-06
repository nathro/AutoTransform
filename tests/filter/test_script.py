# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import json
from unittest.mock import patch, mock_open
from autotransform.filter.script import ScriptFilter
from autotransform.filter.base import FilterName
from autotransform.item.base import Item


class TestScriptFilter:
    """Test cases for the ScriptFilter class."""

    def test_init(self):
        """Test if the ScriptFilter class is correctly initialized with the provided arguments."""
        script_filter = ScriptFilter(
            args=["arg1", "arg2"], script="script.sh", timeout=10, chunk_size=5
        )
        assert script_filter.args == ["arg1", "arg2"]
        assert script_filter.script == "script.sh"
        assert script_filter.timeout == 10
        assert script_filter.chunk_size == 5
        assert script_filter.name == FilterName.SCRIPT

    def test_default_chunk_size(self):
        """Test if the ScriptFilter class correctly defaults chunk_size to None when not provided."""
        script_filter = ScriptFilter(args=["arg1", "arg2"], script="script.sh", timeout=10)
        assert script_filter.chunk_size is None

    @patch("autotransform.filter.script.replace_script_args")
    @patch("autotransform.filter.script.subprocess.run")
    @patch("autotransform.filter.script.json.dump")
    @patch("autotransform.filter.script.json.loads")
    @patch("autotransform.filter.script.TmpFile")
    @patch("builtins.open", new_callable=mock_open, read_data='["key1", "key2"]')
    def test_get_valid_keys(
        self,
        mock_open_file,
        mock_tmp_file,
        mock_json_loads,
        mock_json_dump,
        mock_subprocess_run,
        mock_replace_script_args,
    ):
        """Test if the _get_valid_keys method correctly runs the script and returns the valid keys."""
        # Mock the temporary files
        mock_tmp_file.return_value.__enter__.return_value.name = "tmp_file"

        # Mock the script output
        mock_subprocess_run.return_value.stdout = json.dumps(["key1", "key2"])
        mock_subprocess_run.return_value.stderr = ""
        mock_subprocess_run.return_value.returncode = 0

        # Mock the JSON loads function
        mock_json_loads.return_value = ["key1", "key2"]

        # Create a ScriptFilter and some Items
        script_filter = ScriptFilter(
            args=["<<RESULT_FILE>>", "<<ITEM_FILE>>"], script="script.sh", timeout=10
        )
        items = [Item(key="key1", data={}), Item(key="key2", data={}), Item(key="key3", data={})]

        # Call the _get_valid_keys method and check the result
        result = script_filter._get_valid_keys(items)
        assert result == {"key1", "key2"}

        # Check if the script was run with the correct command
        mock_replace_script_args.assert_called_once_with(
            ["script.sh", "<<RESULT_FILE>>", "<<ITEM_FILE>>"],
            {"<<RESULT_FILE>>": ["tmp_file"], "<<ITEM_FILE>>": ["tmp_file"]},
        )
        mock_subprocess_run.assert_called_once_with(
            mock_replace_script_args.return_value,
            capture_output=True,
            encoding="utf-8",
            check=False,
            timeout=10,
        )

        # Check if the items were dumped to the item file
        mock_json_dump.assert_called_once_with(
            [item.bundle() for item in items], mock_tmp_file.return_value.__enter__.return_value
        )

        # Check if the keys were loaded from the result file
        mock_json_loads.assert_called_once_with(mock_subprocess_run.return_value.stdout)
