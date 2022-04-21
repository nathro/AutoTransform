# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Tests AutoTransformSchema"""

# pylint: disable=too-many-arguments

import pathlib
from typing import List

from git import Repo as GitPython
from mock import patch

from autotransform.batcher.base import Batch, BatchMetadata
from autotransform.batcher.single import SingleBatcher
from autotransform.filter.regex import RegexFilter
from autotransform.input.directory import DirectoryInput
from autotransform.repo.github import GithubRepo
from autotransform.schema.schema import AutoTransformSchema
from autotransform.transformer.regex import RegexTransformer
from autotransform.util.cachedfile import CachedFile


def get_sample_schema() -> AutoTransformSchema:
    """Gets the sample schema being used for testing."""

    repo_root = str(pathlib.Path(__file__).parent.parent.parent.resolve()).replace("\\", "/")
    return AutoTransformSchema(
        DirectoryInput({"path": repo_root}),
        SingleBatcher({"metadata": {"title": "test", "summary": "", "tests": ""}}),
        RegexTransformer({"pattern": "input", "replacement": "inputsource"}),
        filters=[RegexFilter({"pattern": ".*\\.py$"})],
        repo=GithubRepo({"base_branch_name": "master", "full_github_name": "nathro/AutoTransform"}),
    )


ALLOWED_KEYS = ["allowed"]
ALL_KEYS = ["allowed", "not_allowed"]
EXPECTED_METADATA = BatchMetadata({"title": "", "summary": "", "tests": ""})


def mock_input(mocked_get_keys) -> None:
    """Sets up the Input mock."""
    mocked_get_keys.return_value = ALL_KEYS


def mock_filter(mocked_is_valid) -> None:
    """Sets up the Filter mock."""

    def mock_is_valid(key: str) -> bool:
        return key in ALLOWED_KEYS

    mocked_is_valid.side_effect = mock_is_valid


def mock_batcher(mocked_batch) -> None:
    """Sets up the batcher mock."""

    def batch(files: List[CachedFile]) -> List[Batch]:
        return [{"files": files, "metadata": EXPECTED_METADATA}]

    mocked_batch.side_effect = batch


def mock_transformer(mocked_transform) -> None:
    """Sets up the transformer mock."""

    def transform(_: Batch) -> None:
        pass

    mocked_transform.side_effect = transform


def mock_repo(
    mocked_clean,
    mocked_has_changes,
    mocked_submit,
    mocked_rewind,
    should_have_changes: bool,
) -> None:
    """Sets up the repo mock."""

    def clean(_: Batch) -> None:
        pass

    mocked_clean.side_effect = clean

    mocked_has_changes.return_value = should_have_changes

    def submit(_: Batch) -> None:
        pass

    mocked_submit.side_effect = submit

    def rewind(_: Batch) -> None:
        pass

    mocked_rewind.side_effect = rewind


# patches are in reverse order
@patch.object(GitPython, "active_branch")
@patch.object(SingleBatcher, "batch")
@patch.object(RegexFilter, "_is_valid")
@patch.object(DirectoryInput, "get_keys")
def test_get_batches(
    mocked_get_keys,
    mocked_is_valid,
    mocked_batch,
    mocked_active_branch,
):
    """Checks that get_batches properly calls and uses components."""
    # Set up mocks
    mock_input(mocked_get_keys)
    mock_filter(mocked_is_valid)
    mock_batcher(mocked_batch)

    # Run test
    schema = get_sample_schema()
    actual_batch = schema.get_batches()[0]

    # Check Input called
    mocked_get_keys.assert_called_once()

    # Check Filter called
    assert mocked_is_valid.call_count == 2
    filtered_keys = [mock_call.args[0] for mock_call in mocked_is_valid.call_args_list]
    assert filtered_keys == ALL_KEYS

    # Check batcher called
    mocked_batch.assert_called_once()
    batched_paths = [file.path for file in mocked_batch.call_args.args[0]]
    assert batched_paths == ALLOWED_KEYS

    # Check end result
    assert [file.path for file in actual_batch["files"]] == ALLOWED_KEYS
    assert actual_batch["metadata"] == EXPECTED_METADATA


# patches are in reverse order
@patch.object(GithubRepo, "rewind")
@patch.object(GithubRepo, "submit")
@patch.object(GithubRepo, "has_changes")
@patch.object(GithubRepo, "clean")
@patch.object(GitPython, "active_branch")
@patch.object(RegexTransformer, "transform")
@patch.object(SingleBatcher, "batch")
@patch.object(RegexFilter, "_is_valid")
@patch.object(DirectoryInput, "get_keys")
def test_run_with_changes(
    mocked_get_keys,
    mocked_is_valid,
    mocked_batch,
    mocked_transform,
    mocked_active_branch,
    mocked_clean,
    mocked_has_changes,
    mocked_submit,
    mocked_rewind,
):
    """Checks that get_batches properly calls and uses components."""
    # Set up mocks
    mock_input(mocked_get_keys)
    mock_filter(mocked_is_valid)
    mock_batcher(mocked_batch)
    mock_transformer(mocked_transform)
    mock_repo(mocked_clean, mocked_has_changes, mocked_submit, mocked_rewind, True)

    # Run test
    schema = get_sample_schema()
    schema.run()

    # Check Input called
    mocked_get_keys.assert_called_once()

    # Check Filter called
    assert mocked_is_valid.call_count == 2
    filtered_keys = [mock_call.args[0] for mock_call in mocked_is_valid.call_args_list]
    assert filtered_keys == ALL_KEYS

    # Check batcher called
    mocked_batch.assert_called_once()
    batched_paths = [file.path for file in mocked_batch.call_args.args[0]]
    assert batched_paths == ALLOWED_KEYS

    # Check transformer called
    mocked_transform.assert_called_once()
    transformed_path = mocked_transform.call_args.args[0]["files"][0].path
    assert [transformed_path] == ALLOWED_KEYS

    # Check repo calls
    mocked_clean.assert_called_once()
    mocked_has_changes.assert_called_once()
    mocked_submit.assert_called_once()
    mocked_rewind.assert_called_once()


# patches are in reverse order
@patch.object(GithubRepo, "rewind")
@patch.object(GithubRepo, "submit")
@patch.object(GithubRepo, "has_changes")
@patch.object(GithubRepo, "clean")
@patch.object(GitPython, "active_branch")
@patch.object(RegexTransformer, "transform")
@patch.object(SingleBatcher, "batch")
@patch.object(RegexFilter, "_is_valid")
@patch.object(DirectoryInput, "get_keys")
def test_run_with_no_changes(
    mocked_get_keys,
    mocked_is_valid,
    mocked_batch,
    mocked_transform,
    mocked_active_branch,
    mocked_clean,
    mocked_has_changes,
    mocked_submit,
    mocked_rewind,
):
    """Checks that get_batches properly calls and uses components."""
    # Set up mocks
    mock_input(mocked_get_keys)
    mock_filter(mocked_is_valid)
    mock_batcher(mocked_batch)
    mock_transformer(mocked_transform)
    mock_repo(mocked_clean, mocked_has_changes, mocked_submit, mocked_rewind, False)

    # Run test
    schema = get_sample_schema()
    schema.run()

    # Check Input called
    mocked_get_keys.assert_called_once()

    # Check Filter called
    assert mocked_is_valid.call_count == 2
    filtered_keys = [mock_call.args[0] for mock_call in mocked_is_valid.call_args_list]
    assert filtered_keys == ALL_KEYS

    # Check batcher called
    mocked_batch.assert_called_once()
    batched_paths = [file.path for file in mocked_batch.call_args.args[0]]
    assert batched_paths == ALLOWED_KEYS

    # Check transformer called
    mocked_transform.assert_called_once()
    transformed_path = mocked_transform.call_args.args[0]["files"][0].path
    assert [transformed_path] == ALLOWED_KEYS

    # Check repo calls
    mocked_clean.assert_called_once()
    mocked_has_changes.assert_called_once()
    assert mocked_submit.call_count == 0
    assert mocked_rewind.call_count == 0


@patch.object(GitPython, "active_branch")
def test_json_encoding(mocked_active_branch):
    """Checks that the schema is encoded correctly."""

    # pylint: disable=unspecified-encoding

    schema = get_sample_schema()
    schema_json = schema.to_json(pretty=True)
    parent_dir = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/")
    with open(parent_dir + "/data/sample_schema.json", "r") as schema_file:
        actual_json = schema_file.read()
    repo_root = str(pathlib.Path(__file__).parent.parent.parent.resolve()).replace("\\", "/")
    actual_json = actual_json.replace("<<REPO ROOT>>", repo_root)
    assert schema_json == actual_json


@patch.object(GitPython, "active_branch")
def test_json_decoding(mocked_active_branch):
    """Checks that the schema is decoded correctly."""

    # pylint: disable=unspecified-encoding,consider-using-enumerate

    expected_schema = get_sample_schema()
    parent_dir = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/")
    with open(parent_dir + "/data/sample_schema.json", "r") as schema_file:
        actual_json = schema_file.read()
    repo_root = str(pathlib.Path(__file__).parent.parent.parent.resolve()).replace("\\", "/")
    actual_json = actual_json.replace("<<REPO ROOT>>", repo_root)
    actual_schema = AutoTransformSchema.from_json(actual_json)

    # Check Input
    assert type(actual_schema.input) is type(expected_schema.input), "Inputs are not the same"
    assert (
        actual_schema.input.get_params() == expected_schema.input.get_params()
    ), "Inputs do not have the same params"

    # Check batcher
    assert type(actual_schema.batcher) is type(expected_schema.batcher), "Batchers are not the same"
    assert (
        actual_schema.batcher.params == expected_schema.batcher.params
    ), "Batchers do not have the same params"

    # Check transformer
    assert type(actual_schema.transformer) is type(
        expected_schema.transformer
    ), "Transformers are not the same"
    assert (
        actual_schema.transformer.params == expected_schema.transformer.params
    ), "Transformers do not have the same params"

    # Check repo
    if actual_schema.repo is None:
        assert expected_schema.repo is None, "Repo missing from decoded schema"
    assert type(actual_schema.repo) is type(expected_schema.repo), "Repos are not the same"
    assert (
        actual_schema.repo.params == expected_schema.repo.params
    ), "Repos do not have the same params"

    # Check Filters
    for i in range(len(actual_schema.filters)):
        assert i < len(expected_schema.filters), "More Filters present than expected"
        assert type(actual_schema.filters[i]) is type(
            expected_schema.filters[i]
        ), "Filters are not the same"
        assert (
            actual_schema.filters[i].get_params() == expected_schema.filters[i].get_params()
        ), "Filters do not have the same params"

    # Check validators
    for i in range(len(actual_schema.validators)):
        assert i < len(expected_schema.validators), "More Validators present than expected"
        assert type(actual_schema.validators[i]) is type(
            expected_schema.validators[i]
        ), "Validators are not the same"
        assert (
            actual_schema.validators[i].params == expected_schema.validators[i].params
        ), "Validators do not have the same params"

    # Check commands
    for i in range(len(actual_schema.commands)):
        assert i < len(expected_schema.commands), "More Commands present than expected"
        assert type(actual_schema.commands[i]) is type(
            expected_schema.commands[i]
        ), "Commands are not the same"
        assert (
            actual_schema.commands[i].params == expected_schema.commands[i].params
        ), "Commands do not have the same params"

    # Check config
    assert type(actual_schema.config) is type(expected_schema.config), "Configs are not the same"
    assert (
        actual_schema.config.allowed_validation_level
        == expected_schema.config.allowed_validation_level
    ), "Allowed validation level does not match"
