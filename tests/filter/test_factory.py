# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that the Filter's factory is correctly setup."""

from typing import Any, Dict, List

from autotransform.filter.base import FACTORY, FilterName
from autotransform.util.enums import AggregatorType


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory map,
    and only enum values are present."""

    missing_values = [
        filter_name for filter_name in FilterName if filter_name not in FACTORY.get_components()
    ]
    assert not missing_values, "Names missing from factory: " + ", ".join(missing_values)

    extra_values = [
        filter_name for filter_name in FACTORY.get_components() if filter_name not in FilterName
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


def test_encoding_and_decoding() -> None:
    """Tests the encoding and decoding of components."""

    test_components: Dict[FilterName, List[Dict[str, Any]]] = {
        FilterName.AGGREGATE: [
            {"aggregator": AggregatorType.ALL, "filters": [{"name": "regex", "pattern": "test"}]},
            {
                "aggregator": AggregatorType.ALL,
                "filters": [
                    {"name": "regex", "pattern": "test"},
                    {"name": "regex", "pattern": "foo"},
                ],
            },
            {"aggregator": AggregatorType.ANY, "filters": [{"name": "regex", "pattern": "test"}]},
            {
                "aggregator": AggregatorType.ANY,
                "filters": [
                    {"name": "regex", "pattern": "test"},
                    {"name": "regex", "pattern": "foo"},
                ],
            },
        ],
        FilterName.CODEOWNERS: [
            {"codeowners_location": "CODEOWNERS"},
            {"codeowners_location": "CODEOWNERS", "inverted": True},
            {"codeowners_location": "CODEOWNERS", "owner": "nathro"},
            {"codeowners_location": "CODEOWNERS", "owner": "nathro", "inverted": True},
        ],
        FilterName.FILE_EXISTS: [
            {},
            {"check_target_path": True},
        ],
        FilterName.REGEX: [
            {"pattern": "foo"},
            {"pattern": "foo", "inverted": True},
        ],
        FilterName.REGEX_FILE_CONTENT: [
            {"pattern": "foo"},
            {"pattern": "foo", "inverted": True},
        ],
        FilterName.SCRIPT: [
            {"script": "echo", "args": ["foo.json"], "timeout": 360},
            {"script": "echo", "args": ["foo.json"], "timeout": 360, "chunk_size": 100},
        ],
        FilterName.KEY_HASH_SHARD: [
            {"num_shards": 5},
            {"num_shards": 5, "valid_shard": 1},
            {"num_shards": 5, "inverted": True},
            {"num_shards": 5, "valid_shard": 1, "inverted": True},
        ],
    }

    for name in FilterName:
        assert name in test_components, f"No test components for Filter {name}"

    for name, components in test_components.items():
        assert name in FilterName, f"{name} is not a valid FilterName"
        for component in components:
            component_dict = {"name": name} | component
            component_instance = FACTORY.get_instance(component_dict)
            assert (
                component_instance.name == name
            ), f"Testing Filter of name {component_instance.name} for name {name}"
            assert component_dict == component_instance.bundle()
