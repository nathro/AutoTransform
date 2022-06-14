# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for ScriptCommand component."""

import subprocess

import mock

import autotransform
from autotransform.command.script import ScriptCommand
from autotransform.item.base import Item
from autotransform.repo.base import Repo
from autotransform.schema.schema import AutoTransformSchema


@mock.patch.object(subprocess, "run")
def test_no_args(mock_run):
    """Test that subprocess is invoked correctly with no args."""

    proc = mock.create_autospec(subprocess.CompletedProcess)
    proc.stdout = ""
    proc.stderr = ""
    proc.check_returncode.return_value = None
    mock_run.return_value = proc

    command = ScriptCommand(script="black", args=[])
    command.run(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    mock_run.assert_called_once()
    assert mock_run.call_args_list[0].args[0] == ["black"]


@mock.patch.object(subprocess, "run")
def test_key_arg(mock_run):
    """Test that subprocess is invoked correctly with a key argument."""

    proc = mock.create_autospec(subprocess.CompletedProcess)
    proc.stdout = ""
    proc.stderr = ""
    proc.check_returncode.return_value = None
    mock_run.return_value = proc

    command = ScriptCommand(script="black", args=["<<KEY>>"])
    command.run(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    mock_run.assert_called_once()
    assert mock_run.call_args_list[0].args[0] == ["black", '["bar.py", "foo.py"]']


@mock.patch.object(subprocess, "run")
def test_extra_data_arg(mock_run):
    """Test that subprocess is invoked correctly with an extra_data argument."""

    proc = mock.create_autospec(subprocess.CompletedProcess)
    proc.stdout = ""
    proc.stderr = ""
    proc.check_returncode.return_value = None
    mock_run.return_value = proc

    command = ScriptCommand(script="black", args=["<<EXTRA_DATA>>"])
    command.run(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    mock_run.assert_called_once()
    assert mock_run.call_args_list[0].args[0] == [
        "black",
        '{"foo.py": {"test": "TEST"}}',
    ]


@mock.patch.object(subprocess, "run")
def test_metadata_arg(mock_run):
    """Test that subprocess is invoked correctly with a metadata argument."""

    proc = mock.create_autospec(subprocess.CompletedProcess)
    proc.stdout = ""
    proc.stderr = ""
    proc.check_returncode.return_value = None
    mock_run.return_value = proc

    command = ScriptCommand(script="black", args=["<<METADATA>>"])
    command.run(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
            "metadata": {"body": "text"},
        },
        None,
    )

    mock_run.assert_called_once()
    assert mock_run.call_args_list[0].args[0] == [
        "black",
        '{"body": "text"}',
    ]


@mock.patch.object(subprocess, "run")
def test_no_args_per_item(mock_run):
    """Test that subprocess is invoked correctly with no args per item."""

    proc = mock.create_autospec(subprocess.CompletedProcess)
    proc.stdout = ""
    proc.stderr = ""
    proc.check_returncode.return_value = None
    mock_run.return_value = proc

    command = ScriptCommand(script="black", args=[], per_item=True)
    command.run(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    assert mock_run.call_count == 2
    assert mock_run.call_args_list[0].args[0] == ["black"]
    assert mock_run.call_args_list[1].args[0] == ["black"]


@mock.patch.object(subprocess, "run")
def test_key_arg_per_item(mock_run):
    """Test that subprocess is invoked correctly with a key argument per item."""

    proc = mock.create_autospec(subprocess.CompletedProcess)
    proc.stdout = ""
    proc.stderr = ""
    proc.check_returncode.return_value = None
    mock_run.return_value = proc

    command = ScriptCommand(script="black", args=["<<KEY>>"], per_item=True)
    command.run(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    assert mock_run.call_count == 2
    assert mock_run.call_args_list[0].args[0] == ["black", "bar.py"]
    assert mock_run.call_args_list[1].args[0] == ["black", "foo.py"]


@mock.patch.object(subprocess, "run")
def test_extra_data_arg_per_item(mock_run):
    """Test that subprocess is invoked correctly with an extra_data argument per item."""

    proc = mock.create_autospec(subprocess.CompletedProcess)
    proc.stdout = ""
    proc.stderr = ""
    proc.check_returncode.return_value = None
    mock_run.return_value = proc

    command = ScriptCommand(script="black", args=["<<EXTRA_DATA>>"], per_item=True)
    command.run(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    assert mock_run.call_count == 2
    assert mock_run.call_args_list[0].args[0] == ["black", "{}"]
    assert mock_run.call_args_list[1].args[0] == ["black", '{"test": "TEST"}']


@mock.patch.object(subprocess, "run")
def test_metadata_arg_per_item(mock_run):
    """Test that subprocess is invoked correctly with a metadata argument per item."""

    proc = mock.create_autospec(subprocess.CompletedProcess)
    proc.stdout = ""
    proc.stderr = ""
    proc.check_returncode.return_value = None
    mock_run.return_value = proc

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
    assert mock_run.call_args_list[0].args[0] == ["black", '{"body": "text"}']
    assert mock_run.call_args_list[1].args[0] == ["black", '{"body": "text"}']


@mock.patch.object(subprocess, "run")
@mock.patch.object(autotransform, "schema")
def test_key_arg_on_changes(mock_schema, mock_run):
    """Test that subprocess is invoked correctly with a key argument on changes."""

    proc = mock.create_autospec(subprocess.CompletedProcess)
    proc.stdout = ""
    proc.stderr = ""
    proc.check_returncode.return_value = None
    mock_run.return_value = proc

    repo = mock.create_autospec(Repo)
    repo.get_changed_files.return_value = ["fizz.py", "buzz.py"]
    schema = mock.create_autospec(AutoTransformSchema)
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

    mock_run.assert_called_once()
    assert mock_run.call_args_list[0].args[0] == ["black", '["fizz.py", "buzz.py"]']


@mock.patch.object(subprocess, "run")
@mock.patch.object(autotransform, "schema")
def test_key_arg_on_changes_per_item(mock_schema, mock_run):
    """Test that subprocess is invoked correctly with a key argument on changes per item."""

    proc = mock.create_autospec(subprocess.CompletedProcess)
    proc.stdout = ""
    proc.stderr = ""
    proc.check_returncode.return_value = None
    mock_run.return_value = proc

    repo = mock.create_autospec(Repo)
    repo.get_changed_files.return_value = ["fizz.py", "buzz.py"]
    schema = mock.create_autospec(AutoTransformSchema)
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
    assert mock_run.call_args_list[0].args[0] == ["black", "fizz.py"]
    assert mock_run.call_args_list[1].args[0] == ["black", "buzz.py"]
