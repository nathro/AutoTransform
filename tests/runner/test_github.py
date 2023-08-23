# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for the GithubRepo component."""

import json
from unittest.mock import patch

from autotransform.batcher.single import SingleBatcher
from autotransform.change.github import GithubChange
from autotransform.input.empty import EmptyInput
from autotransform.repo.github import GithubRepo
from autotransform.runner.github import GithubRunner
from autotransform.schema.config import SchemaConfig
from autotransform.schema.schema import AutoTransformSchema
from autotransform.transformer.regex import RegexTransformer


@patch("autotransform.util.github.GithubUtils.create_workflow_dispatch")
def test_run(mock_create_dispatch):
    """Tests that running a schema workflow is triggered correctly."""

    schema = AutoTransformSchema(
        input=EmptyInput(),
        batcher=SingleBatcher(title="test"),
        transformer=RegexTransformer(pattern="foo", replacement="bar"),
        config=SchemaConfig(schema_name="test"),
        repo=GithubRepo(base_branch="foo", full_github_name="at/test"),
    )
    mock_create_dispatch.return_value = "test"

    runner = GithubRunner(run_workflow="test.run.yml", update_workflow="test.update.yml")
    runner.run(schema)

    mock_create_dispatch.assert_called_once_with(
        runner.run_workflow, schema.repo.base_branch, {"schema": schema.config.schema_name}
    )


@patch("autotransform.util.github.GithubUtils.create_workflow_dispatch")
@patch("autotransform.change.github.GithubChange.get_schema")
def test_update(mock_get_schema, mock_create_dispatch):
    """Tests that updating a change workflow is triggered correctly."""

    schema = AutoTransformSchema(
        input=EmptyInput(),
        batcher=SingleBatcher(title="test"),
        transformer=RegexTransformer(pattern="foo", replacement="bar"),
        config=SchemaConfig(schema_name="test"),
        repo=GithubRepo(base_branch="foo", full_github_name="at/test"),
    )
    mock_get_schema.return_value = schema

    change = GithubChange(full_github_name="foo", pull_number=1)
    mock_create_dispatch.return_value = "test"

    runner = GithubRunner(run_workflow="test.run.yml", update_workflow="test.update.yml")
    runner.update(change)

    mock_create_dispatch.assert_called_once_with(
        runner.update_workflow, schema.repo.base_branch, {"change": json.dumps(change.bundle())}
    )
