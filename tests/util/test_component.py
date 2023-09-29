# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from unittest.mock import patch
from autotransform.util.component import ComponentModel, ComponentFactory, ComponentImport


# Test the bundle method in the ComponentModel class
def test_component_model_bundle():
    component = ComponentModel()
    assert isinstance(component.bundle(), dict)


# Test the from_data method in the ComponentModel class
def test_component_model_from_data():
    data = {"key": "value"}
    component = ComponentModel.from_data(data)
    assert isinstance(component, ComponentModel)


# Test the get_components method in the ComponentFactory class
def test_component_factory_get_components():
    factory = ComponentFactory({}, ComponentModel, "")
    assert isinstance(factory.get_components(), dict)


# Test the from_console method in the ComponentFactory class
@patch("builtins.input", return_value="yes")
def test_component_factory_from_console(mock_input):
    factory = ComponentFactory({}, ComponentModel, "")
    assert factory.from_console("test", None) is None


# Test the get_class method in the ComponentFactory class
def test_component_factory_get_class():
    factory = ComponentFactory(
        {
            "test": ComponentImport(
                class_name="ComponentModel", module="autotransform.util.component"
            )
        },
        ComponentModel,
        "",
    )
    assert factory.get_class("test") == ComponentModel


# Test the get_custom_components_path method in the ComponentFactory class
def test_component_factory_get_custom_components_path():
    assert ComponentFactory.get_custom_components_path("test.json") == "autotransform/test.json"


# Test the _get_component_class method in the ComponentFactory class
def test_component_factory_get_component_class():
    factory = ComponentFactory({}, ComponentModel, "")
    component_info = ComponentImport(
        class_name="ComponentModel", module="autotransform.util.component"
    )
    assert factory._get_component_class(component_info) == ComponentModel
