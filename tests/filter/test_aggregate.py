# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format
# pylint: disable=redefined-outer-name

"""Tests for AggregateFilter."""

from __future__ import annotations

from typing import List

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


def test_aggregate_filter_with_all_and_empty_filter() -> None:
    """Test AggregateFilter with ALL and a empty filters."""

    filters: List[Filter] = []
    aggregate_filter = AggregateFilter(aggregator=AggregatorType.ALL, filters=filters)
    assert aggregate_filter.is_valid(Item(key="test"))


def test_aggregate_filter_with_all_and_single_filter(valid_filter: ValidFilter) -> None:
    """Test AggregateFilter with ALL and a single filter."""

    filters = [valid_filter]
    aggregate_filter = AggregateFilter(aggregator=AggregatorType.ALL, filters=filters)
    assert aggregate_filter.is_valid(Item(key="test"))


def test_aggregate_filter_with_all_and_valid_filters(valid_filter: ValidFilter) -> None:
    """Test AggregateFilter with ALL and valid filters."""

    filters = [valid_filter, valid_filter]
    aggregate_filter = AggregateFilter(aggregator=AggregatorType.ALL, filters=filters)
    assert aggregate_filter.is_valid(Item(key="test"))


def test_aggregate_filter_with_all_and_invalid_filters(invalid_filter: InvalidFilter) -> None:
    """Test AggregateFilter with ALL and invalid filters."""

    filters = [invalid_filter, invalid_filter]
    aggregate_filter = AggregateFilter(aggregator=AggregatorType.ALL, filters=filters)
    assert not aggregate_filter.is_valid(Item(key="test"))


def test_aggregate_filter_with_all_and_mixed_filters(
    valid_filter: ValidFilter, invalid_filter: InvalidFilter
) -> None:
    """Test AggregateFilter with ALL and mixed filters."""

    filters = [valid_filter, invalid_filter]
    aggregate_filter = AggregateFilter(aggregator=AggregatorType.ALL, filters=filters)
    assert not aggregate_filter.is_valid(Item(key="test"))


def test_aggregate_filter_with_any_and_empty_filter() -> None:
    """Test AggregateFilter with ANY and a empty filters."""

    filters: List[Filter] = []
    aggregate_filter = AggregateFilter(aggregator=AggregatorType.ANY, filters=filters)
    assert not aggregate_filter.is_valid(Item(key="test"))


def test_aggregate_filter_with_any_and_single_filter(valid_filter: ValidFilter) -> None:
    """Test AggregateFilter with ANY and a single filter."""

    filters = [valid_filter]
    aggregate_filter = AggregateFilter(aggregator=AggregatorType.ANY, filters=filters)
    assert aggregate_filter.is_valid(Item(key="test"))


def test_aggregate_filter_with_any_and_valid_filters(valid_filter: ValidFilter) -> None:
    """Test AggregateFilter with ANY and valid filters."""

    filters = [valid_filter, valid_filter]
    aggregate_filter = AggregateFilter(aggregator=AggregatorType.ANY, filters=filters)
    assert aggregate_filter.is_valid(Item(key="test"))


def test_aggregate_filter_with_any_and_invalid_filters(invalid_filter: InvalidFilter) -> None:
    """Test AggregateFilter with ANY and invalid filters."""

    filters = [invalid_filter, invalid_filter]
    aggregate_filter = AggregateFilter(aggregator=AggregatorType.ANY, filters=filters)
    assert not aggregate_filter.is_valid(Item(key="test"))


def test_aggregate_filter_with_any_and_mixed_filters(
    valid_filter: ValidFilter, invalid_filter: InvalidFilter
) -> None:
    """Test AggregateFilter with ANY and mixed filters."""

    filters = [valid_filter, invalid_filter]
    aggregate_filter = AggregateFilter(aggregator=AggregatorType.ANY, filters=filters)
    assert aggregate_filter.is_valid(Item(key="test"))
