# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that the Action's factory is correctly setup."""

from typing import Any, Dict, List

from autotransform.step.action.base import FACTORY, ActionName


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory map,
    and only enum values are present."""

    missing_values = [
        action_name for action_name in ActionName if action_name not in FACTORY.get_components()
    ]
    assert not missing_values, "Names missing from factory: " + ", ".join(missing_values)

    extra_values = [
        action_name for action_name in FACTORY.get_components() if action_name not in ActionName
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

    test_components: Dict[ActionName, List[Dict[str, Any]]] = {
        ActionName.ABANDON: [{}],
        ActionName.ADD_LABELS: [{"labels": ["autotransform"]}],
        ActionName.ADD_OWNERS_AS_REVIEWERS: [{}],
        ActionName.ADD_OWNERS_AS_TEAM_REVIEWERS: [{}],
        ActionName.ADD_REVIEWERS: [
            {"reviewers": ["nathro"]},
            {"team_reviewers": ["slack"]},
            {"reviewers": ["nathro"], "team_reviewers": []},
            {"reviewers": [], "team_reviewers": ["slack"]},
            {"reviewers": ["nathro"], "team_reviewers": ["slack"]},
        ],
        ActionName.COMMENT: [{"body": "This is a cool change!"}],
        ActionName.MERGE: [{}],
        ActionName.NONE: [{}],
        ActionName.REMOVE_LABEL: [{"label": "autotransform"}],
        ActionName.REQUEST: [
            {"url": "test.com"},
            {"url": "test.com", "headers": {"foo": "bar"}},
            {"url": "test.com", "params": {"foo": "bar"}},
            {"url": "test.com", "data": {"foo": "bar"}},
            {"url": "test.com", "post": False},
            {"url": "test.com", "log_response": True},
            {
                "url": "test.com",
                "headers": {"foo": "bar"},
                "params": {"foo": "bar"},
                "data": {"foo": "bar"},
            },
        ],
        ActionName.UPDATE: [{}],
    }

    for name in ActionName:
        assert name in test_components, f"No test components for Action {name}"

    for name, components in test_components.items():
        assert name in ActionName, f"{name} is not a valid ActionName"
        for component in components:
            component_dict = {"name": name} | component
            component_instance = FACTORY.get_instance(component_dict)
            assert (
                component_instance.name == name
            ), f"Testing Action of name {component_instance.name} for name {name}"
            assert component_dict == component_instance.bundle()
