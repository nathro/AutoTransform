# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for ScriptTransformer component."""

import subprocess

import mock
from autotransform.item.base import Item
from autotransform.transformer.script import ScriptTransformer


@mock.patch.object(subprocess, "run")
def test_no_args(mock_run):
    """Test that subprocess is invoked correctly with no args."""

    proc = mock.create_autospec(subprocess.CompletedProcess)
    proc.stdout = ""
    proc.stderr = ""
    proc.check_returncode.return_value = None
    mock_run.return_value = proc

    transformer = ScriptTransformer(script="black", args=[], timeout=100)
    transformer.transform(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
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

    transformer = ScriptTransformer(script="black", args=["<<KEY>>"], timeout=100)
    transformer.transform(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
    )

    mock_run.assert_called_once()
    assert mock_run.call_args_list[0].args[0] == ["black", "bar.py", "foo.py"]


@mock.patch.object(subprocess, "run")
def test_extra_data_arg(mock_run):
    """Test that subprocess is invoked correctly with an extra_data argument."""

    proc = mock.create_autospec(subprocess.CompletedProcess)
    proc.stdout = ""
    proc.stderr = ""
    proc.check_returncode.return_value = None
    mock_run.return_value = proc

    transformer = ScriptTransformer(script="black", args=["<<EXTRA_DATA>>"], timeout=100)
    transformer.transform(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
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

    transformer = ScriptTransformer(script="black", args=["<<METADATA>>"], timeout=100)
    transformer.transform(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
            "metadata": {"body": "text"},
        },
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

    transformer = ScriptTransformer(script="black", args=[], timeout=100, per_item=True)
    transformer.transform(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
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

    transformer = ScriptTransformer(script="black", args=["<<KEY>>"], timeout=100, per_item=True)
    transformer.transform(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
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

    transformer = ScriptTransformer(
        script="black", args=["<<EXTRA_DATA>>"], timeout=100, per_item=True
    )
    transformer.transform(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
        },
    )

    assert mock_run.call_count == 2
    assert mock_run.call_args_list[0].args[0] == ["black", "{}"]
    assert mock_run.call_args_list[1].args[0] == ["black", '{"foo.py": {"test": "TEST"}}']


@mock.patch.object(subprocess, "run")
def test_metadata_arg_per_item(mock_run):
    """Test that subprocess is invoked correctly with a metadata argument per item."""

    proc = mock.create_autospec(subprocess.CompletedProcess)
    proc.stdout = ""
    proc.stderr = ""
    proc.check_returncode.return_value = None
    mock_run.return_value = proc

    transformer = ScriptTransformer(
        script="black", args=["<<METADATA>>"], timeout=100, per_item=True
    )
    transformer.transform(
        {
            "title": "foo",
            "items": [Item(key="bar.py"), Item(key="foo.py", extra_data={"test": "TEST"})],
            "metadata": {"body": "text"},
        },
    )

    assert mock_run.call_count == 2
    assert mock_run.call_args_list[0].args[0] == ["black", '{"body": "text"}']
    assert mock_run.call_args_list[1].args[0] == ["black", '{"body": "text"}']
