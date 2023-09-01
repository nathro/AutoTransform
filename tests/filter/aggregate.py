# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for the AggregateFilter."""

import pytest
from typing import Any, Dict
from autotransform.filter.aggregate import AggregateFilter
from autotransform.filter.base import Filter, FilterName
from autotransform.item.base import Item
from autotransform.step.condition.aggregate import AggregatorType


class TestAggregateFilter:
    """Tests for the AggregateFilter class."""

    @pytest.fixture
    def aggregate_filter(self):
        """Fixture for creating an AggregateFilter instance."""
        return AggregateFilter(aggregator=AggregatorType.ALL, filters=[])

    def test_is_valid_all(self, aggregate_filter):
        """Test the _is_valid method with ALL aggregator."""
        aggregate_filter.aggregator = AggregatorType.ALL
        aggregate_filter.filters = [Filter(is_valid=lambda item: True) for _ in range(3)]
        assert aggregate_filter._is_valid(Item()) is True

        aggregate_filter.filters = [Filter(is_valid=lambda item: False) for _ in range(3)]
        assert aggregate_filter._is_valid(Item()) is False

    def test_is_valid_any(self, aggregate_filter):
        """Test the _is_valid method with ANY aggregator."""
        aggregate_filter.aggregator = AggregatorType.ANY
        aggregate_filter.filters = [Filter(is_valid=lambda item: True) for _ in range(3)]
        assert aggregate_filter._is_valid(Item()) is True

        aggregate_filter.filters = [Filter(is_valid=lambda item: False) for _ in range(3)]
        assert aggregate_filter._is_valid(Item()) is False

    def test_is_valid_unknown(self, aggregate_filter):
        """Test the _is_valid method with an unknown aggregator."""
        aggregate_filter.aggregator = "UNKNOWN"
        with pytest.raises(ValueError):
            aggregate_filter._is_valid(Item())

    def test_from_data(self):
        """Test the from_data class method."""
        data: Dict[str, Any] = {
            "aggregator": "ALL",
            "filters": [{"name": "AGGREGATE", "data": {}}],
        }
        aggregate_filter = AggregateFilter.from_data(data)
        assert isinstance(aggregate_filter, AggregateFilter)
        assert aggregate_filter.aggregator == AggregatorType.ALL
        assert len(aggregate_filter.filters) == 1
        assert aggregate_filter.filters[0].name == FilterName.AGGREGATE
