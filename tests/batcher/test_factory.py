# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that the Batcher's factory is correctly setup."""

from typing import Any, Dict, List

from autotransform.batcher.base import FACTORY, BatcherName


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory map,
    and only enum values are present."""

    factory_components = FACTORY.get_components()
    missing_values = [
        batcher_name for batcher_name in BatcherName if batcher_name not in factory_components
    ]
    assert not missing_values, f"Names missing from factory: {', '.join(missing_values)}"

    extra_values = [
        batcher_name for batcher_name in factory_components if batcher_name not in BatcherName
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


def test_fetching_and_bundling() -> None:
    """Tests the fetching and bundling of components."""

    test_components: Dict[BatcherName, List[Dict[str, Any]]] = {
        BatcherName.CHUNK: [
            {"chunk_size": 5, "title": "foo"},
            {"chunk_size": 5, "title": "foo"},
            {"chunk_size": 5, "title": "foo", "max_chunks": 5},
            {"chunk_size": 5, "title": "foo", "metadata": {"body": "bar"}},
            {"chunk_size": 5, "title": "foo", "max_chunks": 5, "metadata": {"body": "bar"}},
        ],
        BatcherName.CODEOWNERS: [
            {"codeowners_location": "CODEOWNERS", "prefix": "foo"},
            {"codeowners_location": "CODEOWNERS", "prefix": "foo", "metadata": {"body": "bar"}},
        ],
        BatcherName.DIRECTORY: [
            {"prefix": "foo"},
            {"prefix": "foo", "metadata": {"body": "bar"}},
        ],
        BatcherName.EXTRA_DATA: [
            {"group_by": "foo"},
            {"group_by": "foo", "metadata_keys": ["bar"]},
        ],
        BatcherName.FILE_REGEX: [
            {"group_by": "foo{(\\d+)}"},
            {"group_by": "foo{(\\d+)}", "metadata_keys": {"bar": "bar{(\\d+)}"}},
        ],
        BatcherName.SINGLE: [
            {"title": "foo"},
            {"title": "foo", "metadata": {"body": "bar"}},
            {"title": "foo", "skip_empty_batch": True},
            {"title": "foo", "metadata": {"body": "bar"}, "skip_empty_batch": True},
        ],
    }

    for name in BatcherName:
        assert name in test_components, f"No test components for Batcher {name}"

    for name, components in test_components.items():
        assert name in BatcherName, f"{name} is not a valid BatcherName"
        for component in components:
            component_dict = {"name": name, **component}
            component_instance = FACTORY.get_instance(component_dict)
            assert (
                component_instance.name == name
            ), f"Testing Batcher of name {component_instance.name} for name {name}"
            assert component_dict == component_instance.bundle()
