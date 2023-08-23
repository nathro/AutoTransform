# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that the Condition's factory is correctly setup."""

from typing import Any, Dict, List

from autotransform.change.base import ChangeState, ReviewState, TestState
from autotransform.step.condition.base import FACTORY, ConditionName
from autotransform.step.condition.comparison import ComparisonType
from autotransform.util.enums import AggregatorType


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory map,
    and only enum values are present."""

    factory_components = FACTORY.get_components()
    missing_values = [
        condition_name
        for condition_name in ConditionName
        if condition_name not in factory_components
    ]
    assert not missing_values, f"Names missing from factory: {', '.join(missing_values)}"

    extra_values = [
        condition_name
        for condition_name in factory_components
        if condition_name not in ConditionName
    ]
    assert not extra_values, f"Extra names in factory: {', '.join(extra_values)}"


def test_fetching_components():
    """Ensures that all components can be fetched correctly."""

    for component_name in FACTORY.get_components():
        component_class = FACTORY.get_class(component_name)
        assert (
            component_class.name == component_name
        ), f"Component {component_name} has wrong name {component_class.name}"

    for component_name in FACTORY.get_custom_components(strict=True):
        component_class = FACTORY.get_class(component_name)
        assert (
            f"custom/{component_class.name}" == component_name
        ), f"Component {component_name} has wrong name {component_class.name}"


def test_encoding_and_decoding() -> None:
    """Tests the encoding and decoding of components."""

    test_components: Dict[ConditionName, List[Dict[str, Any]]] = {
        ConditionName.AGGREGATE: [
            {
                "aggregator": AggregatorType.ALL,
                "conditions": [],
            },
            {
                "aggregator": AggregatorType.ALL,
                "conditions": [
                    {
                        "name": ConditionName.SCHEMA_NAME,
                        "comparison": ComparisonType.EQUAL,
                        "value": "foo",
                    },
                ],
            },
            {
                "aggregator": AggregatorType.ALL,
                "conditions": [
                    {
                        "name": ConditionName.SCHEMA_NAME,
                        "comparison": ComparisonType.EQUAL,
                        "value": "foo",
                    },
                    {
                        "name": ConditionName.CREATED_AGO,
                        "comparison": ComparisonType.GREATER_THAN_OR_EQUAL,
                        "value": 500,
                    },
                    {
                        "name": ConditionName.UPDATED_AGO,
                        "comparison": ComparisonType.LESS_THAN_OR_EQUAL,
                        "value": 1000,
                    },
                ],
            },
        ],
        ConditionName.CHANGE_STATE: [
            {
                "comparison": ComparisonType.EQUAL,
                "value": ChangeState.OPEN,
            },
        ],
        ConditionName.CREATED_AGO: [
            {
                "comparison": ComparisonType.GREATER_THAN,
                "value": -100,
            },
        ],
        ConditionName.LABELS: [
            {
                "comparison": ComparisonType.CONTAINS,
                "value": "foo",
            },
            {
                "comparison": ComparisonType.EMPTY,
            },
        ],
        ConditionName.MERGEABLE_STATE: [
            {
                "comparison": ComparisonType.EQUAL,
                "value": "has_hooks",
            },
        ],
        ConditionName.REQUEST_STR: [
            {
                "url": "test.com",
                "comparison": ComparisonType.EQUAL,
                "value": "fizz",
            },
            {
                "url": "test.com",
                "headers": {"foo": "bar"},
                "comparison": ComparisonType.EQUAL,
                "value": "fizz",
            },
            {
                "url": "test.com",
                "params": {"foo": "bar"},
                "comparison": ComparisonType.EQUAL,
                "value": "fizz",
            },
            {
                "url": "test.com",
                "data": {"foo": "bar"},
                "comparison": ComparisonType.EQUAL,
                "value": "fizz",
            },
            {
                "url": "test.com",
                "post": False,
                "comparison": ComparisonType.EQUAL,
                "value": "fizz",
            },
            {
                "url": "test.com",
                "log_response": True,
                "comparison": ComparisonType.EQUAL,
                "value": "fizz",
            },
            {
                "url": "test.com",
                "headers": {"foo": "bar"},
                "params": {"foo": "bar"},
                "data": {"foo": "bar"},
                "response_field": "baz",
                "comparison": ComparisonType.EQUAL,
                "value": "fizz",
            },
        ],
        ConditionName.REVIEW_STATE: [
            {
                "comparison": ComparisonType.EQUAL,
                "value": ReviewState.NEEDS_REVIEW,
            },
        ],
        ConditionName.REVIEWERS: [
            {
                "comparison": ComparisonType.CONTAINS,
                "value": "foo",
            },
            {
                "comparison": ComparisonType.EMPTY,
            },
        ],
        ConditionName.SCHEMA_NAME: [
            {
                "comparison": ComparisonType.NOT_EQUAL,
                "value": "foo",
            },
        ],
        ConditionName.TEAM_REVIEWERS: [
            {
                "comparison": ComparisonType.CONTAINS,
                "value": "foo",
            },
            {
                "comparison": ComparisonType.EMPTY,
            },
        ],
        ConditionName.TEST_STATE: [
            {
                "comparison": ComparisonType.EQUAL,
                "value": TestState.PENDING,
            },
        ],
        ConditionName.UPDATED_AGO: [
            {
                "comparison": ComparisonType.LESS_THAN,
                "value": 100,
            },
        ],
    }

    for name in ConditionName:
        assert name in test_components, f"No test components for Condition {name}"

    for name, components in test_components.items():
        assert name in ConditionName, f"{name} is not a valid ConditionName"
        for component in components:
            component_dict = {"name": name, **component}
            component_instance = FACTORY.get_instance(component_dict)
            assert (
                component_instance.name == name
            ), f"Testing Condition of name {component_instance.name} for name {name}"
            assert component_dict == component_instance.bundle()
