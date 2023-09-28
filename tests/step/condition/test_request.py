# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import pytest
from unittest.mock import Mock, patch, ANY
from autotransform.step.condition.request import RequestStrCondition
from autotransform.change.base import Change
from autotransform.step.condition.comparison import ComparisonType
from autotransform.util.request import RequestHandler


@pytest.fixture
def mock_request_handler():
    return Mock(spec=RequestHandler)


@pytest.fixture
def mock_change():
    return Mock(spec=Change)


@patch("autotransform.step.condition.request.RequestHandler", autospec=True)
def test_handler(mock_request_handler_class, mock_request_handler):
    mock_request_handler_class.return_value = mock_request_handler
    condition = RequestStrCondition(
        comparison=ComparisonType.EQUAL, url="http://test.com", value="test"
    )
    assert condition._handler == mock_request_handler


@patch("autotransform.step.condition.request.RequestStrCondition._handler", new_callable=Mock)
def test_get_val_from_change_no_response_field(mock_handler, mock_change):
    mock_handler.get_response.return_value.text = "test response"
    condition = RequestStrCondition(
        comparison=ComparisonType.EQUAL, url="http://test.com", value="test"
    )
    assert condition.get_val_from_change(mock_change) == "test response"


@patch("autotransform.step.condition.request.RequestStrCondition._handler", new_callable=Mock)
def test_get_val_from_change_with_response_field(mock_handler, mock_change):
    mock_handler.get_response.return_value.json.return_value = {"foo": {"bar": "test response"}}
    condition = RequestStrCondition(
        comparison=ComparisonType.EQUAL,
        url="http://test.com",
        value="test",
        response_field="foo//bar",
    )
    assert condition.get_val_from_change(mock_change) == "test response"


@patch("autotransform.step.condition.request.RequestStrCondition._handler", new_callable=Mock)
def test_get_val_from_change_with_nonexistent_response_field(mock_handler, mock_change):
    mock_handler.get_response.return_value.json.return_value = {"foo": {"bar": "test response"}}
    condition = RequestStrCondition(
        comparison=ComparisonType.EQUAL,
        url="http://test.com",
        value="test",
        response_field="foo//baz",
    )
    assert condition.get_val_from_change(mock_change) == "None"


@patch("autotransform.step.condition.request.RequestStrCondition._handler", new_callable=Mock)
def test_get_val_from_change_with_non_json_response(mock_handler, mock_change):
    mock_handler.get_response.return_value.json.side_effect = ValueError
    condition = RequestStrCondition(
        comparison=ComparisonType.EQUAL,
        url="http://test.com",
        value="test",
        response_field="foo//bar",
    )
    with pytest.raises(ValueError):
        condition.get_val_from_change(mock_change)


@patch("autotransform.step.condition.request.RequestHandler", autospec=True)
def test_post_request(mock_request_handler_class, mock_request_handler, mock_change):
    mock_request_handler_class.return_value = mock_request_handler
    condition = RequestStrCondition(
        comparison=ComparisonType.EQUAL, url="http://test.com", value="test", post=True
    )
    condition.get_val_from_change(mock_change)
    mock_request_handler_class.assert_called_once_with(
        url="http://test.com",
        data={},
        headers={},
        params={},
        log_response=False,
        post=True,
        constant_replacers={"env": ANY},
    )


@patch("autotransform.step.condition.request.RequestHandler", autospec=True)
def test_get_request(mock_request_handler_class, mock_request_handler, mock_change):
    mock_request_handler_class.return_value = mock_request_handler
    condition = RequestStrCondition(
        comparison=ComparisonType.EQUAL, url="http://test.com", value="test", post=False
    )
    condition.get_val_from_change(mock_change)
    mock_request_handler_class.assert_called_once_with(
        url="http://test.com",
        data={},
        headers={},
        params={},
        log_response=False,
        post=False,
        constant_replacers={"env": ANY},
    )
