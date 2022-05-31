# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that the Condition's factory is correctly setup."""

import json
from typing import Dict, List

from autotransform.change.base import ChangeState
from autotransform.step.condition.aggregate import AggregateCondition, AggregatorType
from autotransform.step.condition.base import FACTORY, Condition, ConditionName
from autotransform.step.condition.comparison import ComparisonType
from autotransform.step.condition.created import CreatedAgoCondition
from autotransform.step.condition.schema import SchemaNameCondition
from autotransform.step.condition.state import ChangeStateCondition
from autotransform.step.condition.updated import UpdatedAgoCondition


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory map,
    and only enum values are present."""

    missing_values = [
        condition_name
        for condition_name in ConditionName
        if condition_name not in FACTORY.get_components()
    ]
    assert not missing_values, "Names missing from factory: " + ", ".join(missing_values)

    extra_values = [
        condition_name
        for condition_name in FACTORY.get_components()
        if condition_name not in ConditionName
    ]
    assert not extra_values, "Extra names in factory: " + ", ".join(extra_values)


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


def test_encoding_and_decoding():
    """Tests the encoding and decoding of components."""

    test_components: Dict[ConditionName, List[Condition]] = {
        ConditionName.AGGREGATE: [
            AggregateCondition(
                aggregator=AggregatorType.ALL,
                conditions=[],
            ),
            AggregateCondition(
                aggregator=AggregatorType.ALL,
                conditions=[
                    SchemaNameCondition(schema_name="foo", comparison=ComparisonType.NOT_EQUAL),
                ],
            ),
            AggregateCondition(
                aggregator=AggregatorType.ALL,
                conditions=[
                    SchemaNameCondition(schema_name="foo", comparison=ComparisonType.EQUAL),
                    CreatedAgoCondition(comparison=ComparisonType.GREATER_THAN_OR_EQUAL, time=500),
                    UpdatedAgoCondition(comparison=ComparisonType.LESS_THAN_OR_EQUAL, time=1000),
                ],
            ),
        ],
        ConditionName.CHANGE_STATE: [
            ChangeStateCondition(comparison=ComparisonType.EQUAL, state=ChangeState.APPROVED)
        ],
        ConditionName.CREATED_AGO: [
            CreatedAgoCondition(comparison=ComparisonType.GREATER_THAN, time=-100)
        ],
        ConditionName.SCHEMA_NAME: [
            SchemaNameCondition(comparison=ComparisonType.NOT_EQUAL, schema_name="foo")
        ],
        ConditionName.UPDATED_AGO: [
            UpdatedAgoCondition(comparison=ComparisonType.LESS_THAN, time=100)
        ],
    }

    for name in ConditionName:
        assert name in test_components, f"No test components for Condition {name}"

    for name, components in test_components.items():
        assert name in ConditionName, f"{name} is not a valid ConditionName"
        for component in components:
            assert (
                component.name == name
            ), f"Testing condition of name {component.name} for name {name}"
            assert (
                FACTORY.get_instance(json.loads(json.dumps(component.bundle()))) == component
            ), f"Component {component} does not bundle and unbundle correctly"
