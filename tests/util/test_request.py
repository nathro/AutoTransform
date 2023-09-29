# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from unittest.mock import patch, MagicMock
from autotransform.util.request import RequestHandler
import requests


def replacer_func(x):
    """Replacer function for testing."""
    return "replaced"


def test_replace_values():
    """Test the replace_values method with different types of data and replacers."""
    data = {"key1": "<identifier:value>", "key2": {"subkey": "<identifier:value>"}}
    replaced_data = RequestHandler.replace_values(data, "identifier", replacer_func)
    assert replaced_data == {"key1": "replaced", "key2": {"subkey": "replaced"}}


def test_headers_property():
    """Test the _headers property with different types of headers and constant replacers."""
    handler = RequestHandler(
        url="http://test.com",
        headers={"key": "<identifier:value>"},
        constant_replacers={"identifier": replacer_func},
    )
    assert handler._headers == {"key": "replaced"}


def test_params_property():
    """Test the _params property with different types of params and constant replacers."""
    handler = RequestHandler(
        url="http://test.com",
        params={"key": "<identifier:value>"},
        constant_replacers={"identifier": replacer_func},
    )
    assert handler._params == {"key": "replaced"}


def test_data_property():
    """Test the _data property with different types of data and constant replacers."""
    handler = RequestHandler(
        url="http://test.com",
        data={"key": "<identifier:value>"},
        constant_replacers={"identifier": replacer_func},
    )
    assert handler._data == {"key": "replaced"}


@patch("requests.post")
def test_get_response_post(mock_post):
    """Test the get_response method with a POST request."""
    mock_post.return_value = MagicMock(spec=requests.Response, json=lambda: {"key": "value"})
    handler = RequestHandler(url="http://test.com", post=True)
    response = handler.get_response({})
    assert response.json() == {"key": "value"}


@patch("requests.get")
def test_get_response_get(mock_get):
    """Test the get_response method with a GET request."""
    mock_get.return_value = MagicMock(spec=requests.Response, json=lambda: {"key": "value"})
    handler = RequestHandler(url="http://test.com", post=False)
    response = handler.get_response({})
    assert response.json() == {"key": "value"}


@patch("requests.post")
def test_get_response_error(mock_post):
    """Test the get_response method with a request that returns an error."""
    mock_post.return_value = MagicMock(spec=requests.Response, status_code=500)
    handler = RequestHandler(url="http://test.com", post=True)
    response = handler.get_response({})
    assert response.status_code == 500


@patch("requests.post")
@patch("autotransform.event.handler.EventHandler.get")
def test_get_response_log_response_true(mock_get, mock_post):
    """Test the get_response method with the log_response attribute set to True."""
    mock_post.return_value = MagicMock(spec=requests.Response, json=lambda: {"key": "value"})
    handler = RequestHandler(url="http://test.com", post=True, log_response=True)
    handler.get_response({})
    assert mock_get.called


@patch("requests.post")
@patch("autotransform.event.handler.EventHandler.get")
def test_get_response_log_response_false(mock_get, mock_post):
    """Test the get_response method with the log_response attribute set to False."""
    mock_post.return_value = MagicMock(spec=requests.Response, json=lambda: {"key": "value"})
    handler = RequestHandler(url="http://test.com", post=True, log_response=False)
    handler.get_response({})
    assert mock_get.called
