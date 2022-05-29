# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that the Batcher's factory is correctly setup."""

import json
from typing import Dict, List

from autotransform.batcher.base import FACTORY, Batcher, BatcherName
from autotransform.batcher.chunk import ChunkBatcher
from autotransform.batcher.directory import DirectoryBatcher
from autotransform.batcher.single import SingleBatcher


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory map,
    and only enum values are present."""

    missing_values = [
        batcher_type for batcher_type in BatcherName if batcher_type not in FACTORY.get_components()
    ]
    assert not missing_values, "Types missing from factory: " + ", ".join(missing_values)

    extra_values = [
        batcher_type for batcher_type in FACTORY.get_components() if batcher_type not in BatcherName
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

    test_components: Dict[BatcherName, List[Batcher]] = {
        BatcherName.CHUNK: [
            ChunkBatcher(chunk_size=5, title="foo"),
            ChunkBatcher(chunk_size=5, title="foo", max_chunks=5),
            ChunkBatcher(chunk_size=5, title="foo", metadata={"body": "foo"}),
            ChunkBatcher(chunk_size=5, title="foo", max_chunks=5, metadata={"body": "foo"}),
        ],
        BatcherName.DIRECTORY: [
            DirectoryBatcher(prefix="foo"),
            DirectoryBatcher(prefix="foo", metadata={"body": "foo"}),
        ],
        BatcherName.SINGLE: [
            SingleBatcher(title="foo"),
            SingleBatcher(title="foo", metadata={"body": "foo"}),
            SingleBatcher(title="foo", skip_empty_batch=True),
            SingleBatcher(title="foo", metadata={"body": "foo"}, skip_empty_batch=True),
        ],
    }

    for name in BatcherName:
        assert name in test_components, f"No test components for Batcher {name}"

    for name, components in test_components.items():
        assert name in BatcherName, f"{name} is not a valid BatcherName"
        for component in components:
            assert (
                component.name == name
            ), f"Testing batcher of type {component.name} for type {name}"
            assert (
                FACTORY.get_instance(json.loads(json.dumps(component.bundle()))) == component
            ), f"Component {component} does not bundle and unbundle correctly"
