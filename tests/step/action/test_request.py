# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import pytest
from unittest.mock import Mock, patch
from autotransform.change.base import Change
from autotransform.step.action.request import RequestAction
from autotransform.util.request import RequestHandler


class TestRequestAction:
    """Test cases for the RequestAction class."""

    @pytest.fixture
    def mock_change(self):
        """A mock Change object."""
        return Mock(spec=Change)

    @pytest.fixture
    def mock_request_handler(self):
        """A mock RequestHandler object."""
        return Mock(spec=RequestHandler)

    @pytest.fixture
    def request_action(self, mock_request_handler):
        """A RequestAction object with a mocked RequestHandler."""
        with patch(
            "autotransform.step.action.request.RequestHandler", return_value=mock_request_handler
        ):
            return RequestAction(
                url="http://test.com",
                data={"key": "value"},
                headers={"header": "value"},
                params={"param": "value"},
                post=True,
            )

    @patch("requests.post")
    def test_run(self, mock_post, request_action, mock_change, mock_request_handler):
        """Test the run method."""
        mock_response = Mock()
        mock_response.ok = True
        mock_post.return_value = mock_response
        assert request_action.run(mock_change) is True
        mock_response.ok = False
        assert request_action.run(mock_change) is False

    def test_handler(self, request_action, mock_request_handler):
        """Test the _handler cached property."""
        assert isinstance(request_action._handler, RequestHandler)

    def test_post_request(self, request_action):
        """Test if the RequestAction object correctly defaults to a POST request."""
        assert request_action.post is True

    def test_get_request(self):
        """Test if the RequestAction object correctly handles a GET request."""
        request_action = RequestAction(url="http://test.com", post=False)
        assert request_action.post is False

    def test_includes_data_headers_params(self, request_action):
        """Test if the RequestAction object correctly includes data, headers, and params in the request."""
        assert request_action.data == {"key": "value"}
        assert request_action.headers == {"header": "value"}
        assert request_action.params == {"param": "value"}

    def test_log_response(self, request_action):
        """Test if the RequestAction object correctly logs the response."""
        request_action.log_response = True
        assert request_action.log_response is True

    def test_does_not_log_response(self, request_action):
        """Test if the RequestAction object correctly does not log the response."""
        request_action.log_response = False
        assert request_action.log_response is False
