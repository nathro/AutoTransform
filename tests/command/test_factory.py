# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that the Command's factory is correctly setup."""

from typing import Any, Dict, List

from autotransform.command.base import FACTORY, CommandName


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory map,
    and only enum values are present."""

    missing_values = [
        command_name for command_name in CommandName if command_name not in FACTORY.get_components()
    ]
    assert not missing_values, "Names missing from factory: " + ", ".join(missing_values)

    extra_values = [
        command_name for command_name in FACTORY.get_components() if command_name not in CommandName
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


def test_fetching_and_bundling() -> None:
    """Tests the fetching and bundling of components."""

    test_components: Dict[CommandName, List[Dict[str, Any]]] = {
        CommandName.SCRIPT: [
            {"script": "black", "args": ["-l", "100"]},
            {"script": "black", "args": ["-l", "100"], "per_item": True},
            {"script": "black", "args": ["-l", "100"], "run_on_changes": True},
            {"script": "black", "args": ["-l", "100"], "run_pre_validation": True},
            {"script": "black", "args": ["-l", "100"], "per_item": True, "run_on_changes": True},
            {
                "script": "black",
                "args": ["-l", "100"],
                "per_item": True,
                "run_pre_validation": True,
            },
            {
                "script": "black",
                "args": ["-l", "100"],
                "run_on_changes": True,
                "run_pre_validation": True,
            },
            {
                "script": "black",
                "args": ["-l", "100"],
                "per_item": True,
                "run_on_changes": True,
                "run_pre_validation": True,
            },
        ],
    }

    for name in CommandName:
        assert name in test_components, f"No test components for Command {name}"

    for name, components in test_components.items():
        assert name in CommandName, f"{name} is not a valid CommandName"
        for component in components:
            component_dict = {"name": name} | component
            component_instance = FACTORY.get_instance(component_dict)
            assert (
                component_instance.name == name
            ), f"Testing Command of name {component_instance.name} for name {name}"
            assert component_dict == component_instance.bundle()
