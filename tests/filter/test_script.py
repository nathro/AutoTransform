# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for the ScriptFilter class."""

from unittest.mock import patch, MagicMock

from autotransform.event.handler import EventHandler
from autotransform.item.base import Item
from autotransform.filter.script import ScriptFilter


def test_get_valid_keys():
    """Test the _get_valid_keys method with a single Item instance."""
    # Mocking the EventHandler.get() method to return a MagicMock
    with patch.object(EventHandler, "get", return_value=MagicMock()), patch(
        "subprocess.run", return_value=MagicMock(stdout='["key"]')
    ) as mock_subprocess:
        # Creating a ScriptFilter instance with required arguments
        script_filter = ScriptFilter(args=["arg1", "arg2"], script="test_script", timeout=5)

        # Creating a mock Item
        mock_item = MagicMock(spec=Item)
        mock_item.bundle.return_value = {"key": "value"}

        # Testing _get_valid_keys method
        result = script_filter._get_valid_keys([mock_item])

        # Asserting that the method was called with the correct arguments
        mock_subprocess.assert_called_once()

        # Asserting that the result is as expected
        assert result == set(["key"])


def test_get_valid_keys_with_chunk_size():
    """Test the _get_valid_keys method with a chunk size and two Item instances."""
    # Mocking the EventHandler.get() method to return a MagicMock
    with patch.object(EventHandler, "get", return_value=MagicMock()), patch(
        "subprocess.run", return_value=MagicMock(stdout='["key1", "key2"]')
    ) as mock_subprocess:
        # Creating a ScriptFilter instance with required arguments and chunk size
        script_filter = ScriptFilter(
            args=["arg1", "arg2"], script="test_script", timeout=5, chunk_size=2
        )

        # Creating mock Items
        mock_item1 = MagicMock(spec=Item)
        mock_item1.bundle.return_value = {"key1": "value1"}
        mock_item2 = MagicMock(spec=Item)
        mock_item2.bundle.return_value = {"key2": "value2"}

        # Testing _get_valid_keys method
        result = script_filter._get_valid_keys([mock_item1, mock_item2])

        # Asserting that the method was called with the correct arguments
        mock_subprocess.assert_called_once()

        # Asserting that the result is as expected
        assert result == set(["key1", "key2"])
