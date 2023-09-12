# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from unittest.mock import Mock, patch
from autotransform.change.base import Change
from autotransform.step.condition.comparison import ComparisonType
from autotransform.step.condition.request import RequestStrCondition
from autotransform.util.request import RequestHandler


def test_request_str_condition_initialization():
    condition = RequestStrCondition(
        comparison=ComparisonType.EQUAL,
        url="http://test.com",
        value="test_value",
        data={"key": "value"},
        headers={"header": "value"},
        log_response=True,
        params={"param": "value"},
        post=False,
        response_field="field",
    )
    assert condition.comparison == ComparisonType.EQUAL
    assert condition.url == "http://test.com"
    assert condition.value == "test_value"
    assert condition.data == {"key": "value"}
    assert condition.headers == {"header": "value"}
    assert condition.log_response is True
    assert condition.params == {"param": "value"}
    assert condition.post is False
    assert condition.response_field == "field"


def test_handler_method():
    condition = RequestStrCondition(
        comparison=ComparisonType.EQUAL, url="http://test.com", value="test_value"
    )
    assert isinstance(condition._handler, RequestHandler)


@patch("autotransform.step.condition.request.RequestHandler.get_response")
def test_get_val_from_change(mock_get_response):
    mock_response = Mock()
    mock_response.text = "test_response"
    mock_get_response.return_value = mock_response

    condition = RequestStrCondition(
        comparison=ComparisonType.EQUAL, url="http://test.com", value="test_value"
    )
    change = Mock(spec=Change)
    assert condition.get_val_from_change(change) == "test_response"


@patch("autotransform.step.condition.request.RequestHandler.get_response")
def test_get_val_from_change_with_response_field(mock_get_response):
    mock_response = Mock()
    mock_response.json.return_value = {"field": "test_response"}
    mock_get_response.return_value = mock_response

    condition = RequestStrCondition(
        comparison=ComparisonType.EQUAL,
        url="http://test.com",
        value="test_value",
        response_field="field",
    )
    change = Mock(spec=Change)
    assert condition.get_val_from_change(change) == "test_response"
