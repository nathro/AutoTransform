# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import pytest
from unittest.mock import MagicMock, call, patch
from autotransform.batcher.base import Batch
from autotransform.item.base import Item
from autotransform.transformer.single import SingleTransformer


class TestSingleTransformer:
    """Test cases for the SingleTransformer class."""

    class SingleTransformerMock(SingleTransformer):
        """A mock class that inherits from SingleTransformer for testing purposes."""

        def _transform_item(self, item: Item) -> None:
            pass

    @patch.object(SingleTransformerMock, "_transform_item", new_callable=MagicMock)
    def test_transform_with_items(self, mock_transform_item):
        """Test that transform method correctly handles a Batch with Items."""
        transformer = self.SingleTransformerMock()

        items = [Item(key="item1"), Item(key="item2"), Item(key="item3")]
        batch = Batch(items=items)

        transformer.transform(batch)

        calls = [call(item) for item in items]
        mock_transform_item.assert_has_calls(calls)

    @patch.object(SingleTransformerMock, "_transform_item", new_callable=MagicMock)
    def test_transform_without_items(self, mock_transform_item):
        """Test that transform method correctly handles a Batch without Items."""
        transformer = self.SingleTransformerMock()

        batch = Batch()

        transformer.transform(batch)

        mock_transform_item.assert_not_called()

    @patch.object(SingleTransformerMock, "_transform_item", new_callable=MagicMock)
    def test_transform_with_invalid_data(self, mock_transform_item):
        """Test that transform method correctly handles a Batch with invalid data."""
        transformer = self.SingleTransformerMock()

        batch = Batch(items=[None, "invalid"])

        transformer.transform(batch)

        calls = [call(None), call("invalid")]
        mock_transform_item.assert_has_calls(calls)

    def test_instantiate_abstract_class(self):
        """Test that an error is raised when trying to instantiate the abstract class."""
        with pytest.raises(TypeError):
            SingleTransformer()  # pylint: disable=abstract-class-instantiated
