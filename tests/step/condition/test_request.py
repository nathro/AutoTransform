# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from unittest.mock import patch, Mock
from autotransform.step.condition.comparison import ComparisonType
from autotransform.step.condition.request import RequestStrCondition
from autotransform.util.request import RequestHandler


def test_handler():
    condition = RequestStrCondition(
        comparison=ComparisonType.EQUAL,
        url="http://test.com",
        value="test",
        data={"key": "value"},
        headers={"header": "value"},
        params={"param": "value"},
        post=True,
        log_response=False,
    )
    assert isinstance(condition._handler, RequestHandler)


@patch("autotransform.util.request.RequestHandler.get_response")
def test_get_val_from_change_no_response_field(mock_get_response):
    mock_get_response.return_value.text = "test response"
    condition = RequestStrCondition(
        comparison=ComparisonType.EQUAL, url="http://test.com", value="test"
    )
    change = Mock()
    assert condition.get_val_from_change(change) == "test response"


@patch("autotransform.util.request.RequestHandler.get_response")
def test_get_val_from_change_with_response_field(mock_get_response):
    mock_get_response.return_value.json.return_value = {"field": "test response"}
    condition = RequestStrCondition(
        comparison=ComparisonType.EQUAL, url="http://test.com", value="test", response_field="field"
    )
    change = Mock()
    assert condition.get_val_from_change(change) == "test response"


@patch("autotransform.util.request.RequestHandler.get_response")
def test_get_val_from_change_with_nested_response_field(mock_get_response):
    mock_get_response.return_value.json.return_value = {"field": {"nested_field": "test response"}}
    condition = RequestStrCondition(
        comparison=ComparisonType.EQUAL,
        url="http://test.com",
        value="test",
        response_field="field//nested_field",
    )
    change = Mock()
    assert condition.get_val_from_change(change) == "test response"


# Add more tests here following the same pattern
