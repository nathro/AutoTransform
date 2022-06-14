# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for ScriptValidator component."""

import subprocess
from typing import List

import mock

import autotransform
from autotransform.item.base import Item
from autotransform.repo.base import Repo
from autotransform.schema.schema import AutoTransformSchema
from autotransform.validator.base import ValidationResultLevel
from autotransform.validator.script import ScriptValidator

# pylint: disable=unused-argument


@mock.patch.object(subprocess, "run")
def test_no_args(mock_run):
    """Test that subprocess is invoked correctly with no args."""

    proc = mock.create_autospec(subprocess.CompletedProcess)
    proc.stdout = ""
    proc.stderr = ""
    proc.returncode = 0
    mock_run.return_value = proc

    validator = ScriptValidator(script="black", args=[])
    result = validator.check(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    assert result.level == ValidationResultLevel.NONE
    mock_run.assert_called_once()
    assert mock_run.call_args_list[0].args[0] == ["black"]


@mock.patch.object(subprocess, "run")
def test_key_arg(mock_run):
    """Test that subprocess is invoked correctly with a key argument."""

    proc = mock.create_autospec(subprocess.CompletedProcess)
    proc.stdout = ""
    proc.stderr = ""
    proc.returncode = 0
    mock_run.return_value = proc

    validator = ScriptValidator(script="black", args=["<<KEY>>"])
    result = validator.check(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    assert result.level == ValidationResultLevel.NONE
    mock_run.assert_called_once()
    assert mock_run.call_args_list[0].args[0] == ["black", '["bar.py", "foo.py"]']


@mock.patch.object(subprocess, "run")
def test_extra_data_arg(mock_run):
    """Test that subprocess is invoked correctly with an extra_data argument."""

    proc = mock.create_autospec(subprocess.CompletedProcess)
    proc.stdout = ""
    proc.stderr = ""
    proc.returncode = 0
    mock_run.return_value = proc

    validator = ScriptValidator(script="black", args=["<<EXTRA_DATA>>"])
    result = validator.check(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    assert result.level == ValidationResultLevel.NONE
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
    proc.returncode = 0
    mock_run.return_value = proc

    validator = ScriptValidator(script="black", args=["<<METADATA>>"])
    result = validator.check(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
            "metadata": {"body": "text"},
        },
        None,
    )

    assert result.level == ValidationResultLevel.NONE
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
    proc.returncode = 0
    mock_run.return_value = proc

    validator = ScriptValidator(script="black", args=[], per_item=True)
    result = validator.check(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    assert result.level == ValidationResultLevel.NONE
    assert mock_run.call_count == 2
    assert mock_run.call_args_list[0].args[0] == ["black"]
    assert mock_run.call_args_list[1].args[0] == ["black"]


@mock.patch.object(subprocess, "run")
def test_key_arg_per_item(mock_run):
    """Test that subprocess is invoked correctly with a key argument per item."""

    proc = mock.create_autospec(subprocess.CompletedProcess)
    proc.stdout = ""
    proc.stderr = ""
    proc.returncode = 0
    mock_run.return_value = proc

    validator = ScriptValidator(script="black", args=["<<KEY>>"], per_item=True)
    result = validator.check(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    assert result.level == ValidationResultLevel.NONE
    assert mock_run.call_count == 2
    assert mock_run.call_args_list[0].args[0] == ["black", "bar.py"]
    assert mock_run.call_args_list[1].args[0] == ["black", "foo.py"]


@mock.patch.object(subprocess, "run")
def test_extra_data_arg_per_item(mock_run):
    """Test that subprocess is invoked correctly with an extra_data argument per item."""

    proc = mock.create_autospec(subprocess.CompletedProcess)
    proc.stdout = ""
    proc.stderr = ""
    proc.returncode = 0
    mock_run.return_value = proc

    validator = ScriptValidator(script="black", args=["<<EXTRA_DATA>>"], per_item=True)
    result = validator.check(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    assert result.level == ValidationResultLevel.NONE
    assert mock_run.call_count == 2
    assert mock_run.call_args_list[0].args[0] == ["black", "{}"]
    assert mock_run.call_args_list[1].args[0] == ["black", '{"test": "TEST"}']


@mock.patch.object(subprocess, "run")
def test_metadata_arg_per_item(mock_run):
    """Test that subprocess is invoked correctly with a metadata argument per item."""

    proc = mock.create_autospec(subprocess.CompletedProcess)
    proc.stdout = ""
    proc.stderr = ""
    proc.returncode = 0
    mock_run.return_value = proc

    validator = ScriptValidator(script="black", args=["<<METADATA>>"], per_item=True)
    result = validator.check(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
            "metadata": {"body": "text"},
        },
        None,
    )

    assert result.level == ValidationResultLevel.NONE
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
    proc.returncode = 0
    mock_run.return_value = proc

    repo = mock.create_autospec(Repo)
    repo.get_changed_files.return_value = ["fizz.py", "buzz.py"]
    schema = mock.create_autospec(AutoTransformSchema)
    schema.repo = repo
    mock_schema.current = schema

    validator = ScriptValidator(script="black", args=["<<KEY>>"], run_on_changes=True)
    result = validator.check(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py")],
        },
        None,
    )

    assert result.level == ValidationResultLevel.NONE
    mock_run.assert_called_once()
    assert mock_run.call_args_list[0].args[0] == ["black", '["fizz.py", "buzz.py"]']


@mock.patch.object(subprocess, "run")
@mock.patch.object(autotransform, "schema")
def test_key_arg_on_changes_per_item(mock_schema, mock_run):
    """Test that subprocess is invoked correctly with a key argument on changes per item."""

    proc = mock.create_autospec(subprocess.CompletedProcess)
    proc.stdout = ""
    proc.stderr = ""
    proc.returncode = 0
    mock_run.return_value = proc

    repo = mock.create_autospec(Repo)
    repo.get_changed_files.return_value = ["fizz.py", "buzz.py"]
    schema = mock.create_autospec(AutoTransformSchema)
    schema.repo = repo
    mock_schema.current = schema

    validator = ScriptValidator(
        script="black", args=["<<KEY>>"], per_item=True, run_on_changes=True
    )
    result = validator.check(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py")],
        },
        None,
    )

    assert result.level == ValidationResultLevel.NONE
    assert mock_run.call_count == 2
    assert mock_run.call_args_list[0].args[0] == ["black", "fizz.py"]
    assert mock_run.call_args_list[1].args[0] == ["black", "buzz.py"]


@mock.patch.object(subprocess, "run")
def test_fails(mock_run):
    """Test that a failure code causes the right result."""

    proc = mock.create_autospec(subprocess.CompletedProcess)
    proc.stdout = ""
    proc.stderr = ""
    proc.returncode = 1
    mock_run.return_value = proc

    validator = ScriptValidator(script="black", args=[])
    result = validator.check(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    assert result.level == ValidationResultLevel.ERROR


@mock.patch.object(subprocess, "run")
def test_per_item_all_fails(mock_run):
    """Test that a failure code for all Items causes the right result."""

    proc = mock.create_autospec(subprocess.CompletedProcess)
    proc.stdout = ""
    proc.stderr = ""
    proc.returncode = 1
    mock_run.return_value = proc

    validator = ScriptValidator(script="black", args=[], per_item=True)
    result = validator.check(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    mock_run.assert_called_once()
    assert result.level == ValidationResultLevel.ERROR


@mock.patch.object(subprocess, "run")
def test_per_item_first_fails(mock_run):
    """Test that a failure code for the first Item causes the right result."""

    def get_proc(
        args: List[str], capture_output: bool = False, encoding: str = "UTF-8", check: bool = False
    ) -> subprocess.CompletedProcess:
        proc = mock.create_autospec(subprocess.CompletedProcess)
        proc.stdout = ""
        proc.stderr = ""
        if args[1] == "foo.py":
            proc.returncode = 0
        else:
            proc.returncode = 1
        return proc

    mock_run.side_effect = get_proc

    validator = ScriptValidator(script="black", args=["<<KEY>>"], per_item=True)
    result = validator.check(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    mock_run.assert_called_once()
    assert result.level == ValidationResultLevel.ERROR


@mock.patch.object(subprocess, "run")
def test_per_item_second_fails(mock_run):
    """Test that a failure code for the second Item causes the right result."""

    def get_proc(
        args: List[str], capture_output: bool = False, encoding: str = "UTF-8", check: bool = False
    ) -> subprocess.CompletedProcess:
        proc = mock.create_autospec(subprocess.CompletedProcess)
        proc.stdout = ""
        proc.stderr = ""
        if args[1] == "bar.py":
            proc.returncode = 0
        else:
            proc.returncode = 1
        return proc

    mock_run.side_effect = get_proc

    validator = ScriptValidator(script="black", args=["<<KEY>>"], per_item=True)
    result = validator.check(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    assert mock_run.call_count == 2
    assert result.level == ValidationResultLevel.ERROR
