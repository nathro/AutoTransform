# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import os
import json
import time
from unittest.mock import patch
from autotransform.event.handler import EventHandler
from autotransform.event.logginglevel import LoggingLevel


class MockEvent:
    """Mock Event class for testing."""

    def __init__(self, logging_level, message, color_override=None):
        self.logging_level = logging_level
        self.message = message
        self.color_override = color_override
        self.create_time = time.time()

    def get_logging_level(self):
        return self.logging_level

    def get_message(self):
        return self.message

    def get_color_override(self):
        return self.color_override


class TestEventHandler:
    """Test cases for the EventHandler class."""

    def setup_method(self):
        """Reset EventHandler singleton instance before each test."""
        EventHandler._EventHandler__instance = None

    def test_get_without_env_var(self):
        """Test get method without AUTO_TRANSFORM_EVENT_HANDLER environment variable."""
        handler = EventHandler.get()
        assert isinstance(handler, EventHandler)

    @patch("importlib.import_module")
    def test_get_with_valid_env_var(self, mock_import):
        """Test get method with valid AUTO_TRANSFORM_EVENT_HANDLER environment variable."""
        mock_import.return_value = EventHandler
        os.environ["AUTO_TRANSFORM_EVENT_HANDLER"] = json.dumps(
            {"class_name": "EventHandler", "module": "autotransform.event.handler"}
        )
        handler = EventHandler.get()
        assert isinstance(handler, EventHandler)

    @patch("importlib.import_module")
    def test_get_with_invalid_env_var(self, mock_import):
        """Test get method with invalid AUTO_TRANSFORM_EVENT_HANDLER environment variable."""
        mock_import.side_effect = ImportError
        os.environ["AUTO_TRANSFORM_EVENT_HANDLER"] = json.dumps(
            {"class_name": "InvalidHandler", "module": "invalid.module"}
        )
        handler = EventHandler.get()
        assert isinstance(handler, EventHandler)

    def test_set_logging_level(self):
        """Test set_logging_level method."""
        handler = EventHandler.get()
        handler.set_logging_level(LoggingLevel.ERROR)
        assert handler._logging_level == LoggingLevel.ERROR

    @patch("builtins.print")
    def test_handle_with_lower_level_event(self, mock_print):
        """Test handle method with event of lower logging level."""
        handler = EventHandler.get()
        handler.set_logging_level(LoggingLevel.ERROR)
        event = MockEvent(LoggingLevel.INFO, "Test event")
        handler.handle(event)
        mock_print.assert_not_called()

    @patch("builtins.print")
    def test_handle_with_higher_level_event(self, mock_print):
        """Test handle method with event of higher or equal logging level."""
        handler = EventHandler.get()
        handler.set_logging_level(LoggingLevel.INFO)
        event = MockEvent(LoggingLevel.ERROR, "Test event")
        handler.handle(event)
        mock_print.assert_called()

    @patch("builtins.print")
    def test_output_to_cli_with_color_override(self, mock_print):
        """Test output_to_cli method with color override."""
        event = MockEvent(LoggingLevel.INFO, "Test event", color_override="Test color")
        EventHandler.output_to_cli(event)
        mock_print.assert_called()

    @patch("builtins.print")
    def test_output_to_cli_without_color_override(self, mock_print):
        """Test output_to_cli method without color override."""
        event = MockEvent(LoggingLevel.INFO, "Test event")
        EventHandler.output_to_cli(event)
        mock_print.assert_called()
