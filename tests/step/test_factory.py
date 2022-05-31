# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that the Step's factory is correctly setup."""

import json
from typing import Dict, List

from autotransform.step.action import ActionType
from autotransform.step.base import FACTORY, Step, StepName
from autotransform.step.condition.aggregate import AggregateCondition, AggregatorType
from autotransform.step.condition.comparison import ComparisonType
from autotransform.step.condition.created import CreatedAgoCondition
from autotransform.step.condition.updated import UpdatedAgoCondition
from autotransform.step.conditional import ConditionalStep


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory map,
    and only enum values are present."""

    missing_values = [
        step_name for step_name in StepName if step_name not in FACTORY.get_components()
    ]
    assert not missing_values, "Names missing from factory: " + ", ".join(missing_values)

    extra_values = [
        step_name for step_name in FACTORY.get_components() if step_name not in StepName
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

    test_components: Dict[StepName, List[Step]] = {
        StepName.CONDITIONAL: [
            ConditionalStep(
                action=ActionType.ABANDON,
                condition=CreatedAgoCondition(comparison=ComparisonType.GREATER_THAN, time=500),
            ),
            ConditionalStep(
                action=ActionType.ABANDON,
                condition=AggregateCondition(
                    aggregator=AggregatorType.ALL,
                    conditions=[
                        CreatedAgoCondition(comparison=ComparisonType.GREATER_THAN, time=500),
                        UpdatedAgoCondition(
                            comparison=ComparisonType.GREATER_THAN_OR_EQUAL, time=100
                        ),
                    ],
                ),
            ),
        ]
    }

    for name in StepName:
        assert name in test_components, f"No test components for Step {name}"

    for name, components in test_components.items():
        assert name in StepName, f"{name} is not a valid StepName"
        for component in components:
            assert component.name == name, f"Testing step of name {component.name} for name {name}"
            assert (
                FACTORY.get_instance(json.loads(json.dumps(component.bundle()))) == component
            ), f"Component {component} does not bundle and unbundle correctly"
