# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for ScriptCommand component."""

import subprocess
from unittest.mock import patch, create_autospec

from autotransform.command.script import ScriptCommand
from autotransform.item.base import Item
from autotransform.repo.base import Repo
from autotransform.schema.schema import AutoTransformSchema

import autotransform


def setup_mock_run(mock_run):
    """Setup mock for subprocess run."""
    proc = create_autospec(subprocess.CompletedProcess)
    proc.stdout = ""
    proc.stderr = ""
    proc.check_returncode.return_value = None
    mock_run.return_value = proc


@patch.object(subprocess, "run")
def test_no_args(mock_run):
    """Test that subprocess is invoked correctly with no args."""
    setup_mock_run(mock_run)

    command = ScriptCommand(script="black", args=[])
    command.run(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    mock_run.assert_called_once_with(
        ["black"], capture_output=True, encoding="utf-8", check=False, timeout=None
    )


@patch.object(subprocess, "run")
def test_key_arg(mock_run):
    """Test that subprocess is invoked correctly with a key argument."""
    setup_mock_run(mock_run)

    command = ScriptCommand(script="black", args=["<<KEY>>"])
    command.run(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    mock_run.assert_called_once_with(
        ["black", "bar.py", "foo.py"],
        capture_output=True,
        encoding="utf-8",
        check=False,
        timeout=None,
    )


@patch.object(subprocess, "run")
def test_extra_data_arg(mock_run):
    """Test that subprocess is invoked correctly with an extra_data argument."""
    setup_mock_run(mock_run)

    command = ScriptCommand(script="black", args=["<<EXTRA_DATA>>"])
    command.run(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    mock_run.assert_called_once_with(
        ["black", '{"foo.py": {"test": "TEST"}}'],
        capture_output=True,
        encoding="utf-8",
        check=False,
        timeout=None,
    )


@patch.object(subprocess, "run")
def test_metadata_arg(mock_run):
    """Test that subprocess is invoked correctly with a metadata argument."""
    setup_mock_run(mock_run)

    command = ScriptCommand(script="black", args=["<<METADATA>>"])
    command.run(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
            "metadata": {"body": "text"},
        },
        None,
    )

    mock_run.assert_called_once_with(
        ["black", '{"body": "text"}'],
        capture_output=True,
        encoding="utf-8",
        check=False,
        timeout=None,
    )


@patch.object(subprocess, "run")
def test_no_args_per_item(mock_run):
    """Test that subprocess is invoked correctly with no args per item."""
    setup_mock_run(mock_run)

    command = ScriptCommand(script="black", args=[], per_item=True)
    command.run(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    assert mock_run.call_count == 2
    mock_run.assert_any_call(
        ["black"], capture_output=True, encoding="utf-8", check=False, timeout=None
    )


@patch.object(subprocess, "run")
def test_key_arg_per_item(mock_run):
    """Test that subprocess is invoked correctly with a key argument per item."""
    setup_mock_run(mock_run)

    command = ScriptCommand(script="black", args=["<<KEY>>"], per_item=True)
    command.run(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    assert mock_run.call_count == 2
    mock_run.assert_any_call(
        ["black", "bar.py"], capture_output=True, encoding="utf-8", check=False, timeout=None
    )
    mock_run.assert_any_call(
        ["black", "foo.py"], capture_output=True, encoding="utf-8", check=False, timeout=None
    )


@patch.object(subprocess, "run")
def test_extra_data_arg_per_item(mock_run):
    """Test that subprocess is invoked correctly with an extra_data argument per item."""
    setup_mock_run(mock_run)

    command = ScriptCommand(script="black", args=["<<EXTRA_DATA>>"], per_item=True)
    command.run(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    assert mock_run.call_count == 2
    mock_run.assert_any_call(
        ["black", "{}"], capture_output=True, encoding="utf-8", check=False, timeout=None
    )
    mock_run.assert_any_call(
        ["black", '{"foo.py": {"test": "TEST"}}'],
        capture_output=True,
        encoding="utf-8",
        check=False,
        timeout=None,
    )


@patch.object(subprocess, "run")
def test_metadata_arg_per_item(mock_run):
    """Test that subprocess is invoked correctly with a metadata argument per item."""
    setup_mock_run(mock_run)

    command = ScriptCommand(script="black", args=["<<METADATA>>"], per_item=True)
    command.run(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
            "metadata": {"body": "text"},
        },
        None,
    )

    assert mock_run.call_count == 2
    mock_run.assert_any_call(
        ["black", '{"body": "text"}'],
        capture_output=True,
        encoding="utf-8",
        check=False,
        timeout=None,
    )


@patch.object(subprocess, "run")
@patch.object(autotransform, "schema")
def test_key_arg_on_changes(mock_schema, mock_run):
    """Test that subprocess is invoked correctly with a key argument on changes."""
    setup_mock_run(mock_run)

    repo = create_autospec(Repo)
    repo.get_changed_files.return_value = ["fizz.py", "buzz.py"]
    schema = create_autospec(AutoTransformSchema)
    schema.repo = repo
    mock_schema.current = schema

    command = ScriptCommand(script="black", args=["<<KEY>>"], run_on_changes=True)
    command.run(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py")],
        },
        None,
    )

    mock_run.assert_called_once_with(
        ["black", "fizz.py", "buzz.py"],
        capture_output=True,
        encoding="utf-8",
        check=False,
        timeout=None,
    )


@patch.object(subprocess, "run")
@patch.object(autotransform, "schema")
def test_key_arg_on_changes_per_item(mock_schema, mock_run):
    """Test that subprocess is invoked correctly with a key argument on changes per item."""
    setup_mock_run(mock_run)

    repo = create_autospec(Repo)
    repo.get_changed_files.return_value = ["fizz.py", "buzz.py"]
    schema = create_autospec(AutoTransformSchema)
    schema.repo = repo
    mock_schema.current = schema

    command = ScriptCommand(script="black", args=["<<KEY>>"], per_item=True, run_on_changes=True)
    command.run(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py")],
        },
        None,
    )

    assert mock_run.call_count == 2
    mock_run.assert_any_call(
        ["black", "fizz.py"], capture_output=True, encoding="utf-8", check=False, timeout=None
    )
    mock_run.assert_any_call(
        ["black", "buzz.py"], capture_output=True, encoding="utf-8", check=False, timeout=None
    )
