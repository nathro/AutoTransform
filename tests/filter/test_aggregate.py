# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format
# pylint: disable=redefined-outer-name

"""Tests for AggregateFilter."""

import pytest
from autotransform.filter.aggregate import AggregateFilter
from autotransform.filter.base import Filter
from autotransform.item.base import Item
from autotransform.step.condition.aggregate import AggregatorType


class ValidFilter(Filter):
    """A dummy Filter that always returns True."""

    def _is_valid(self, _item: Item) -> bool:
        return True


class InvalidFilter(Filter):
    """A dummy Filter that always returns False."""

    def _is_valid(self, _item: Item) -> bool:
        return False


@pytest.fixture
def valid_filter() -> ValidFilter:
    """A simple pytest fixture.

    Returns:
        ValidFilter: The filter to use in the fixture.
    """

    return ValidFilter()


@pytest.fixture
def invalid_filter() -> InvalidFilter:
    """A simple pytest fixture.

    Returns:
        InvalidFilter: The filter to use in the fixture.
    """

    return InvalidFilter()


@pytest.mark.parametrize(
    "aggregator, filters, expected",
    [
        (AggregatorType.ALL, [], True),
        (AggregatorType.ALL, [ValidFilter()], True),
        (AggregatorType.ALL, [ValidFilter(), ValidFilter()], True),
        (AggregatorType.ALL, [InvalidFilter(), InvalidFilter()], False),
        (AggregatorType.ALL, [ValidFilter(), InvalidFilter()], False),
        (AggregatorType.ANY, [], False),
        (AggregatorType.ANY, [ValidFilter()], True),
        (AggregatorType.ANY, [ValidFilter(), ValidFilter()], True),
        (AggregatorType.ANY, [InvalidFilter(), InvalidFilter()], False),
        (AggregatorType.ANY, [ValidFilter(), InvalidFilter()], True),
    ],
)
def test_aggregate_filter(aggregator, filters, expected):
    """Test AggregateFilter with different aggregators and filters."""

    aggregate_filter = AggregateFilter(aggregator=aggregator, filters=filters)
    assert aggregate_filter.is_valid(Item(key="test")) == expected
