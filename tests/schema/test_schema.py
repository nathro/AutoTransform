# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Tests AutoTransformSchema"""

import pathlib

from autotransform.batcher.single import SingleBatcher
from autotransform.filter.extension import ExtensionFilter, Extensions
from autotransform.input.directory import DirectoryInput
from autotransform.repo.github import GithubRepo
from autotransform.schema.schema import AutoTransformSchema
from autotransform.transformer.regex import RegexTransformer


def get_sample_schema() -> AutoTransformSchema:
    """Gets the sample schema being used for testing."""
    return AutoTransformSchema(
        DirectoryInput({"path": "C:/repos/autotransform"}),
        SingleBatcher({"metadata": {"title": "test", "summary": "", "tests": ""}}),
        RegexTransformer({"pattern": "input", "replacement": "inputsource"}),
        filters=[ExtensionFilter({"extensions": [Extensions.PYTHON]})],
        repo=GithubRepo(
            {"path": "C:/repos/autotransform", "full_github_name": "nathro/AutoTransform"}
        ),
    )


def test_json_encoding():
    """Checks that the schema is encoded correctly."""

    # pylint: disable=unspecified-encoding

    schema = get_sample_schema()
    schema_json = schema.to_json(pretty=True)
    parent_dir = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/")
    with open(parent_dir + "/data/sample_schema.json", "r") as schema_file:
        actual_json = schema_file.read()
    assert schema_json == actual_json


def test_json_decoding():
    """Checks that the schema is decoded correctly."""

    # pylint: disable=unspecified-encoding,consider-using-enumerate

    expected_schema = get_sample_schema()
    parent_dir = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/")
    with open(parent_dir + "/data/sample_schema.json", "r") as schema_file:
        actual_json = schema_file.read()
    actual_schema = AutoTransformSchema.from_json(actual_json)

    # Check input
    assert type(actual_schema.input) is type(expected_schema.input), "Inputs are not the same"
    assert (
        actual_schema.input.params == expected_schema.input.params
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

    # Check filters
    for i in range(len(actual_schema.filters)):
        assert i < len(expected_schema.filters), "More filters present than expected"
        assert type(actual_schema.filters[i]) is type(
            expected_schema.filters[i]
        ), "Filters are not the same"
        assert (
            actual_schema.filters[i].params == expected_schema.filters[i].params
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
