# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that the Transformer's factory is correctly setup."""

from typing import Any, Dict, List

from autotransform.transformer.base import FACTORY, TransformerName


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory map,
    and only enum values are present."""

    missing_values = [
        transformer_name
        for transformer_name in TransformerName
        if transformer_name not in FACTORY.get_components()
    ]
    assert not missing_values, "Names missing from factory: " + ", ".join(missing_values)

    extra_values = [
        transformer_name
        for transformer_name in FACTORY.get_components()
        if transformer_name not in TransformerName
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

    test_components: Dict[TransformerName, List[Dict[str, Any]]] = {
        TransformerName.JSCODESHIFT: [
            {"js_transform": "myTransform.js"},
            {"js_transform": "myTransform.js", "args": ["--foo", "bar"]},
            {"js_transform": "myTransform.js", "timeout": 300},
            {"js_transform": "myTransform.js", "args": ["--foo", "bar"], "timeout": 300},
        ],
        TransformerName.LIBCST: [
            {"command_module": "libcst.codemod", "command_name": "codemod_command"},
            {
                "command_module": "libcst.codemod",
                "command_name": "codemod_command",
                "command_args": {"test": "foo"},
            },
        ],
        TransformerName.REGEX: [{"pattern": "foo", "replacement": "bar"}],
        TransformerName.SCRIPT: [
            {"script": "black", "args": ["-l", "100"], "timeout": 100},
            {"script": "black", "args": ["-l", "100"], "timeout": 100, "per_item": True},
        ],
    }

    for name in TransformerName:
        assert name in test_components, f"No test components for Transformer {name}"

    for name, components in test_components.items():
        assert name in TransformerName, f"{name} is not a valid TransformerName"
        for component in components:
            component_dict = {"name": name} | component
            component_instance = FACTORY.get_instance(component_dict)
            assert (
                component_instance.name == name
            ), f"Testing Transformer of name {component_instance.name} for name {name}"
            assert component_dict == component_instance.bundle()
