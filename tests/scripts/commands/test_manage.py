# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import pytest
from argparse import ArgumentParser, Namespace
from unittest.mock import patch, MagicMock
from autotransform.scripts.commands import manage
from autotransform.event.handler import EventHandler
from autotransform.event.logginglevel import LoggingLevel
from autotransform.util.manager import Manager


def test_add_args():
    parser = ArgumentParser()
    manage.add_args(parser)
    args = parser.parse_args(["--path", "/path/to/file", "--verbose", "--local"])
    assert args.path == "/path/to/file"
    assert args.verbose is True
    assert args.debug is False
    assert args.run_local is True


def test_manage_command_main():
    args = Namespace(path="/path/to/file", verbose=True, debug=False, run_local=True)
    with patch.object(EventHandler, "get") as mock_get, patch.object(Manager, "read") as mock_read:
        mock_event_handler = MagicMock()
        mock_get.return_value = mock_event_handler
        mock_manager = MagicMock()
        mock_read.return_value = mock_manager
        mock_manager.run = MagicMock()
        manage.manage_command_main(args)
        mock_get.assert_called_once()
        mock_event_handler.set_logging_level.assert_called_once_with(LoggingLevel.VERBOSE)
        mock_read.assert_called_once_with("/path/to/file")
        mock_event_handler.handle.assert_called()
        mock_manager.run.assert_called_once_with(True)


def test_manage_command_main_no_path():
    args = Namespace(path=None, verbose=False, debug=False, run_local=False)
    with patch.object(EventHandler, "get") as mock_get, patch.object(Manager, "read") as mock_read:
        mock_event_handler = MagicMock()
        mock_get.return_value = mock_event_handler
        mock_manager = MagicMock()
        mock_read.return_value = mock_manager
        mock_manager.run = MagicMock()
        manage.manage_command_main(args)
        mock_get.assert_called_once()
        mock_event_handler.set_logging_level.assert_not_called()
        mock_read.assert_called()  # called with default path
        mock_event_handler.handle.assert_called()
        mock_manager.run.assert_called_once_with(False)


@pytest.mark.parametrize(
    "path,verbose,debug,run_local",
    [
        ("/path/to/nonexistent/file", False, False, False),
        ("/path/to/invalid.json", True, False, True),
        ("/path/to/invalid/manager", False, True, False),
    ],
)
def test_manage_command_main_error_cases(path, verbose, debug, run_local):
    args = Namespace(path=path, verbose=verbose, debug=debug, run_local=run_local)
    with pytest.raises(Exception):
        manage.manage_command_main(args)
