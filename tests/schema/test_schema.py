# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests AutoTransformSchema"""

# pylint: disable=too-many-arguments

import json
import pathlib
from typing import Any, List, Mapping, Optional, Sequence

from autotransform.batcher.base import Batch
from autotransform.batcher.single import SingleBatcher
from autotransform.change.base import Change
from autotransform.filter.regex import RegexFilter
from autotransform.input.directory import DirectoryInput
from autotransform.item.base import Item
from autotransform.repo.github import GithubRepo
from autotransform.schema.config import SchemaConfig
from autotransform.schema.schema import AutoTransformSchema
from autotransform.transformer.regex import RegexTransformer
from git import Head
from mock import patch

ALLOWED_ITEMS = [Item(key="allowed")]
ALL_ITEMS = [Item(key="allowed"), Item(key="not_allowed")]
EXPECTED_METADATA = {"summary": "", "tests": ""}
EXPECTED_TITLE = "test"


def get_sample_schema() -> AutoTransformSchema:
    """Gets the sample schema being used for testing."""

    repo_root = str(pathlib.Path(__file__).parent.parent.parent.resolve()).replace("\\", "/")
    return AutoTransformSchema(
        input=DirectoryInput(paths=[repo_root]),
        batcher=SingleBatcher(title=EXPECTED_TITLE, metadata=EXPECTED_METADATA),
        transformer=RegexTransformer(pattern="input", replacement="inputsource"),
        config=SchemaConfig(schema_name="Sample", owners=["foo", "bar"]),
        filters=[RegexFilter(pattern=".*\\.py$")],
        repo=GithubRepo(
            base_branch="master",
            full_github_name="nathro/AutoTransform",
            hide_autotransform_docs=True,
        ),
    )


def mock_input(mocked_get_items) -> None:
    """Sets up the Input mock."""
    mocked_get_items.return_value = ALL_ITEMS


def mock_filter(mocked_is_valid) -> None:
    """Sets up the Filter mock."""

    def mock_is_valid(item: Item) -> bool:
        return item.key in [item.key for item in ALLOWED_ITEMS]

    mocked_is_valid.side_effect = mock_is_valid


def mock_batcher(mocked_batch) -> None:
    """Sets up the batcher mock."""

    def batch(items: Sequence[Item]) -> List[Batch]:
        return [{"title": EXPECTED_TITLE, "items": items, "metadata": EXPECTED_METADATA}]

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

    def clean(_batch: Batch) -> None:
        pass

    mocked_clean.side_effect = clean

    mocked_has_changes.return_value = should_have_changes

    # pylint: disable=unused-argument

    def submit(
        _batch: Batch, _transform_data: Optional[Mapping[str, Any]], change: Optional[Change] = None
    ) -> None:
        pass

    mocked_submit.side_effect = submit

    def rewind(_batch: Batch) -> None:
        pass

    mocked_rewind.side_effect = rewind


# patches are in reverse order
@patch.object(Head, "checkout")
@patch.object(SingleBatcher, "batch")
@patch.object(RegexFilter, "_is_valid")
@patch.object(DirectoryInput, "get_items")
def test_get_batches(
    mocked_get_items,
    mocked_is_valid,
    mocked_batch,
    _mocked_checkout,
):
    """Checks that get_batches properly calls and uses components."""
    # Set up mocks
    mock_input(mocked_get_items)
    mock_filter(mocked_is_valid)
    mock_batcher(mocked_batch)

    # Run test
    schema = get_sample_schema()
    actual_batch = schema.get_batches()[0]

    # Check Input called
    mocked_get_items.assert_called_once()

    # Check Filter called
    assert mocked_is_valid.call_count == 2
    filtered_keys = [mock_call.args[0].key for mock_call in mocked_is_valid.call_args_list]
    assert filtered_keys == [item.key for item in ALL_ITEMS]

    # Check batcher called
    mocked_batch.assert_called_once()
    batched_keys = [item.key for item in mocked_batch.call_args.args[0]]
    assert batched_keys == [item.key for item in ALLOWED_ITEMS]

    # Check end result
    actual_keys = [item.key for item in actual_batch["items"]]
    assert actual_keys == [item.key for item in ALLOWED_ITEMS]
    assert actual_batch["metadata"] == EXPECTED_METADATA
    assert actual_batch["title"] == EXPECTED_TITLE


# patches are in reverse order
@patch.object(GithubRepo, "rewind")
@patch.object(GithubRepo, "submit")
@patch.object(GithubRepo, "has_changes")
@patch.object(GithubRepo, "clean")
@patch.object(Head, "checkout")
@patch.object(RegexTransformer, "transform")
@patch.object(SingleBatcher, "batch")
@patch.object(RegexFilter, "_is_valid")
@patch.object(DirectoryInput, "get_items")
def test_run_with_changes(
    mocked_get_items,
    mocked_is_valid,
    mocked_batch,
    mocked_transform,
    _mocked_checkout,
    mocked_clean,
    mocked_has_changes,
    mocked_submit,
    mocked_rewind,
):
    """Checks that get_batches properly calls and uses components."""
    # Set up mocks
    mock_input(mocked_get_items)
    mock_filter(mocked_is_valid)
    mock_batcher(mocked_batch)
    mock_transformer(mocked_transform)
    mock_repo(mocked_clean, mocked_has_changes, mocked_submit, mocked_rewind, True)

    # Run test
    schema = get_sample_schema()
    schema.run()

    # Check Input called
    mocked_get_items.assert_called_once()

    # Check Filter called
    assert mocked_is_valid.call_count == 2
    filtered_keys = [mock_call.args[0].key for mock_call in mocked_is_valid.call_args_list]
    assert filtered_keys == [item.key for item in ALL_ITEMS]

    # Check batcher called
    mocked_batch.assert_called_once()
    batched_keys = [item.key for item in mocked_batch.call_args.args[0]]
    assert batched_keys == [item.key for item in ALLOWED_ITEMS]

    # Check transformer called
    mocked_transform.assert_called_once()
    transformed_key = mocked_transform.call_args.args[0]["items"][0].key
    assert [transformed_key] == [item.key for item in ALLOWED_ITEMS]

    # Check repo calls
    assert mocked_clean.call_count == 0
    mocked_has_changes.assert_called_once()
    mocked_submit.assert_called_once()
    assert mocked_rewind.call_count == 2


# patches are in reverse order
@patch.object(GithubRepo, "rewind")
@patch.object(GithubRepo, "submit")
@patch.object(GithubRepo, "has_changes")
@patch.object(GithubRepo, "clean")
@patch.object(Head, "checkout")
@patch.object(RegexTransformer, "transform")
@patch.object(SingleBatcher, "batch")
@patch.object(RegexFilter, "_is_valid")
@patch.object(DirectoryInput, "get_items")
def test_run_with_no_changes(
    mocked_get_items,
    mocked_is_valid,
    mocked_batch,
    mocked_transform,
    _mocked_checkout,
    mocked_clean,
    mocked_has_changes,
    mocked_submit,
    mocked_rewind,
):
    """Checks that get_batches properly calls and uses components."""
    # Set up mocks
    mock_input(mocked_get_items)
    mock_filter(mocked_is_valid)
    mock_batcher(mocked_batch)
    mock_transformer(mocked_transform)
    mock_repo(mocked_clean, mocked_has_changes, mocked_submit, mocked_rewind, False)

    # Run test
    schema = get_sample_schema()
    schema.run()

    # Check Input called
    mocked_get_items.assert_called_once()

    # Check Filter called
    assert mocked_is_valid.call_count == 2
    filtered_keys = [mock_call.args[0].key for mock_call in mocked_is_valid.call_args_list]
    assert filtered_keys == [item.key for item in ALL_ITEMS]

    # Check batcher called
    mocked_batch.assert_called_once()
    batched_keys = [item.key for item in mocked_batch.call_args.args[0]]
    assert batched_keys == [item.key for item in ALLOWED_ITEMS]

    # Check transformer called
    mocked_transform.assert_called_once()
    transformed_key = mocked_transform.call_args.args[0]["items"][0].key
    assert [transformed_key] == [item.key for item in ALLOWED_ITEMS]

    # Check repo calls
    assert mocked_clean.call_count == 0
    mocked_has_changes.assert_called_once()
    assert mocked_submit.call_count == 0
    mocked_rewind.assert_called_once()


@patch.object(Head, "checkout")
def test_json_encoding(_mocked_checkout):
    """Checks that the schema is encoded correctly."""

    # pylint: disable=unspecified-encoding

    schema = get_sample_schema()
    schema_json = json.dumps(schema.bundle(), indent=4)
    print(schema_json)
    parent_dir = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/")
    with open(f"{parent_dir}/data/sample_schema.json", "r") as schema_file:
        actual_json = schema_file.read()
    repo_root = str(pathlib.Path(__file__).parent.parent.parent.resolve()).replace("\\", "/")
    actual_json = actual_json.replace("<<REPO ROOT>>", repo_root)
    assert schema_json == actual_json


@patch.object(Head, "checkout")
def test_json_decoding(_mocked_checkout):
    """Checks that the schema is decoded correctly."""

    # pylint: disable=unspecified-encoding,consider-using-enumerate

    expected_schema = get_sample_schema()
    parent_dir = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/")
    with open(f"{parent_dir}/data/sample_schema.json", "r") as schema_file:
        actual_json = schema_file.read()
    repo_root = str(pathlib.Path(__file__).parent.parent.parent.resolve()).replace("\\", "/")
    actual_json = actual_json.replace("<<REPO ROOT>>", repo_root)
    actual_schema = AutoTransformSchema.from_data(json.loads(actual_json))

    assert actual_schema == expected_schema
