# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for ScriptValidator component."""

import subprocess
from typing import List, Optional

import mock
from autotransform.item.base import Item
from autotransform.repo.base import Repo
from autotransform.schema.schema import AutoTransformSchema
from autotransform.validator.base import ValidationResultLevel
from autotransform.validator.script import ScriptValidator

import autotransform

# pylint: disable=unused-argument


def create_mock_process(returncode: int):
    """Create a mock subprocess.CompletedProcess object with the specified return code."""
    proc = mock.create_autospec(subprocess.CompletedProcess)
    proc.stdout = ""
    proc.stderr = ""
    proc.returncode = returncode
    return proc


@mock.patch.object(subprocess, "run")
def test_no_args(mock_run):
    """Test that subprocess is invoked correctly with no args."""
    mock_run.return_value = create_mock_process(0)

    validator = ScriptValidator(script="black", args=[])
    result = validator.check(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    assert result.level == ValidationResultLevel.NONE
    mock_run.assert_called_once_with(
        ["black"], capture_output=True, encoding="utf-8", check=False, timeout=None
    )


@mock.patch.object(subprocess, "run")
def test_key_arg(mock_run):
    """Test that subprocess is invoked correctly with a key argument."""
    mock_run.return_value = create_mock_process(0)

    validator = ScriptValidator(script="black", args=["<<KEY>>"])
    result = validator.check(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    assert result.level == ValidationResultLevel.NONE
    mock_run.assert_called_once_with(
        ["black", "bar.py", "foo.py"],
        capture_output=True,
        encoding="utf-8",
        check=False,
        timeout=None,
    )


@mock.patch.object(subprocess, "run")
def test_extra_data_arg(mock_run):
    """Test that subprocess is invoked correctly with an extra_data argument."""
    mock_run.return_value = create_mock_process(0)

    validator = ScriptValidator(script="black", args=["<<EXTRA_DATA>>"])
    result = validator.check(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    assert result.level == ValidationResultLevel.NONE
    mock_run.assert_called_once_with(
        ["black", '{"foo.py": {"test": "TEST"}}'],
        capture_output=True,
        encoding="utf-8",
        check=False,
        timeout=None,
    )


@mock.patch.object(subprocess, "run")
def test_metadata_arg(mock_run):
    """Test that subprocess is invoked correctly with a metadata argument."""
    mock_run.return_value = create_mock_process(0)

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
    mock_run.assert_called_once_with(
        ["black", '{"body": "text"}'],
        capture_output=True,
        encoding="utf-8",
        check=False,
        timeout=None,
    )


@mock.patch.object(subprocess, "run")
def test_no_args_per_item(mock_run):
    """Test that subprocess is invoked correctly with no args per item."""
    mock_run.return_value = create_mock_process(0)

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
    mock_run.assert_any_call(
        ["black"], capture_output=True, encoding="utf-8", check=False, timeout=None
    )


@mock.patch.object(subprocess, "run")
def test_key_arg_per_item(mock_run):
    """Test that subprocess is invoked correctly with a key argument per item."""
    mock_run.return_value = create_mock_process(0)

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
    mock_run.assert_any_call(
        ["black", "bar.py"], capture_output=True, encoding="utf-8", check=False, timeout=None
    )
    mock_run.assert_any_call(
        ["black", "foo.py"], capture_output=True, encoding="utf-8", check=False, timeout=None
    )


@mock.patch.object(subprocess, "run")
def test_extra_data_arg_per_item(mock_run):
    """Test that subprocess is invoked correctly with an extra_data argument per item."""
    mock_run.return_value = create_mock_process(0)

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


@mock.patch.object(subprocess, "run")
def test_metadata_arg_per_item(mock_run):
    """Test that subprocess is invoked correctly with a metadata argument per item."""
    mock_run.return_value = create_mock_process(0)

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
    mock_run.assert_any_call(
        ["black", '{"body": "text"}'],
        capture_output=True,
        encoding="utf-8",
        check=False,
        timeout=None,
    )


@mock.patch.object(subprocess, "run")
@mock.patch.object(autotransform, "schema")
def test_key_arg_on_changes(mock_schema, mock_run):
    """Test that subprocess is invoked correctly with a key argument on changes."""
    mock_run.return_value = create_mock_process(0)

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
    mock_run.assert_called_once_with(
        ["black", "fizz.py", "buzz.py"],
        capture_output=True,
        encoding="utf-8",
        check=False,
        timeout=None,
    )


@mock.patch.object(subprocess, "run")
@mock.patch.object(autotransform, "schema")
def test_key_arg_on_changes_per_item(mock_schema, mock_run):
    """Test that subprocess is invoked correctly with a key argument on changes per item."""
    mock_run.return_value = create_mock_process(0)

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
    mock_run.assert_any_call(
        ["black", "fizz.py"], capture_output=True, encoding="utf-8", check=False, timeout=None
    )
    mock_run.assert_any_call(
        ["black", "buzz.py"], capture_output=True, encoding="utf-8", check=False, timeout=None
    )


@mock.patch.object(subprocess, "run")
def test_fails(mock_run):
    """Test that a failure code causes the right result."""
    mock_run.return_value = create_mock_process(1)

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
    mock_run.return_value = create_mock_process(1)

    validator = ScriptValidator(script="black", args=[], per_item=True)
    result = validator.check(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    assert result.level == ValidationResultLevel.ERROR


@mock.patch.object(subprocess, "run")
def test_per_item_first_fails(mock_run):
    """Test that a failure code for the first Item causes the right result."""

    def get_proc(
        args: List[str],
        capture_output: bool = False,
        encoding: str = "utf-8",
        check: bool = False,
        timeout: Optional[int] = None,
    ) -> subprocess.CompletedProcess:
        return create_mock_process(0 if args[1] == "foo.py" else 1)

    mock_run.side_effect = get_proc

    validator = ScriptValidator(script="black", args=["<<KEY>>"], per_item=True)
    result = validator.check(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    assert result.level == ValidationResultLevel.ERROR


@mock.patch.object(subprocess, "run")
def test_per_item_second_fails(mock_run):
    """Test that a failure code for the second Item causes the right result."""

    def get_proc(
        args: List[str],
        capture_output: bool = False,
        encoding: str = "utf-8",
        check: bool = False,
        timeout: Optional[int] = None,
    ) -> subprocess.CompletedProcess:
        return create_mock_process(0 if args[1] == "bar.py" else 1)

    mock_run.side_effect = get_proc

    validator = ScriptValidator(script="black", args=["<<KEY>>"], per_item=True)
    result = validator.check(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
        None,
    )

    assert result.level == ValidationResultLevel.ERROR
