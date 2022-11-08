# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for the GitRepo component."""

import mock

import autotransform
from autotransform.repo.git import GitRepo
from autotransform.schema.config import SchemaConfig
from autotransform.schema.schema import AutoTransformSchema


def test_get_changed_files():
    """Tests that the repo returns changed files from status"""

    assert GitRepo.get_changed_files_from_status("  \n ") == []
    assert GitRepo.get_changed_files_from_status(" M foo.py") == ["foo.py"]
    assert GitRepo.get_changed_files_from_status(" A foo.py") == ["foo.py"]
    assert GitRepo.get_changed_files_from_status(" D foo.py") == ["foo.py"]
    assert GitRepo.get_changed_files_from_status("?? foo.py") == ["foo.py"]
    assert GitRepo.get_changed_files_from_status(
        "?? foo.py\n M bar.py\n A fizz.py\n D buzz.py"
    ) == ["foo.py", "bar.py", "fizz.py", "buzz.py"]


@mock.patch.object(autotransform, "schema")
def test_get_branch_name(mock_schema):
    """Tests getting the name of the branch to use."""

    schema = mock.create_autospec(AutoTransformSchema)
    schema.config = SchemaConfig(schema_name="Test Schema")
    mock_schema.current = schema

    assert GitRepo.get_branch_name("Test Title") == "AUTO_TRANSFORM__Test_Schema__Test_Title"
    assert GitRepo.get_branch_name("[1/2] Test") == "AUTO_TRANSFORM__Test_Schema__1_2_Test"


@mock.patch.object(autotransform, "schema")
def test_get_commit_message(mock_schema):
    """Tests getting the commit message to use."""

    schema = mock.create_autospec(AutoTransformSchema)
    schema.config = SchemaConfig(schema_name="Test Schema")
    mock_schema.current = schema

    assert GitRepo.get_commit_message("Test") == "[AutoTransform][Test Schema] Test"
    assert GitRepo.get_commit_message("[1/2] Test") == "[AutoTransform][Test Schema][1/2] Test"
