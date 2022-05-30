# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that the Filter's factory is correctly setup."""

import json
from typing import Dict, List

from autotransform.filter.base import FACTORY, Filter, FilterName
from autotransform.filter.key_hash_shard import KeyHashShardFilter
from autotransform.filter.regex import RegexFileContentFilter, RegexFilter


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory map,
    and only enum values are present."""

    missing_values = [
        filter_type for filter_type in FilterName if filter_type not in FACTORY.get_components()
    ]
    assert not missing_values, "Types missing from factory: " + ", ".join(missing_values)

    extra_values = [
        filter_type for filter_type in FACTORY.get_components() if filter_type not in FilterName
    ]
    assert not extra_values, "Extra types in factory: " + ", ".join(extra_values)


def test_fetching_components():
    """Ensures that all components can be fetched correctly."""

    for component_type in FACTORY.get_components():
        component_class = FACTORY.get_class(component_type)
        assert (
            component_class.name == component_type
        ), f"Component {component_type} has wrong type {component_class.name}"

    for component_type in FACTORY.get_custom_components(strict=True):
        component_class = FACTORY.get_class(component_type)
        assert (
            f"custom/{component_class.name}" == component_type
        ), f"Component {component_type} has wrong type {component_class.name}"


def test_encoding_and_decoding():
    """Tests the encoding and decoding of components."""

    test_components: Dict[FilterName, List[Filter]] = {
        FilterName.REGEX: [
            RegexFilter(pattern="foo"),
            RegexFilter(pattern="foo", inverted=True),
        ],
        FilterName.REGEX_FILE_CONTENT: [
            RegexFileContentFilter(pattern="foo"),
            RegexFileContentFilter(pattern="foo", inverted=True),
        ],
        FilterName.KEY_HASH_SHARD: [
            KeyHashShardFilter(num_shards=5, valid_shard=1),
            KeyHashShardFilter(num_shards=5, valid_shard=1, inverted=True),
        ],
    }

    for name in FilterName:
        assert name in test_components, f"No test components for Filter {name}"

    for name, components in test_components.items():
        assert name in FilterName, f"{name} is not a valid FilterName"
        for component in components:
            assert (
                component.name == name
            ), f"Testing filter of type {component.name} for type {name}"
            assert (
                FACTORY.get_instance(json.loads(json.dumps(component.bundle()))) == component
            ), f"Component {component} does not bundle and unbundle correctly"
