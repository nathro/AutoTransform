# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that the Item's factory is correctly setup."""

from typing import Any, Dict, List

from autotransform.item.base import FACTORY, ItemName


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory map,
    and only enum values are present."""

    factory_components = FACTORY.get_components()
    missing_values = [item_name for item_name in ItemName if item_name not in factory_components]
    assert not missing_values, f"Names missing from factory: {', '.join(missing_values)}"

    extra_values = [item_name for item_name in factory_components if item_name not in ItemName]
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

    test_components: Dict[ItemName, List[Dict[str, Any]]] = {
        ItemName.FILE: [
            {"key": "foo"},
            {"key": "foo", "extra_data": {"body": "bar"}},
        ],
        ItemName.GENERIC: [
            {"key": "foo"},
            {"key": "foo", "extra_data": {"body": "bar"}},
        ],
    }

    for name in ItemName:
        assert name in test_components, f"No test components for Item {name}"

    for name, components in test_components.items():
        for component in components:
            component_dict = {"name": name, **component}
            component_instance = FACTORY.get_instance(component_dict)
            assert (
                component_instance.name == name
            ), f"Testing Item of name {component_instance.name} for name {name}"
            assert component_dict == component_instance.bundle()
