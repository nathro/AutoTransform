# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import pytest
from autotransform.item.file import FileItem
from autotransform.model.openai import OpenAIModel
from autotransform.validator.base import ValidationResult
from unittest.mock import patch, MagicMock


def test_prompts_must_contain_at_least_one_item():
    with pytest.raises(ValueError):
        OpenAIModel(prompts=[])

    assert OpenAIModel.prompts_must_contain_at_least_one_item(["prompt"])


def test_temperature_must_be_valid():
    with pytest.raises(ValueError):
        OpenAIModel(prompts=["prompt"], temperature=1.5)

    assert OpenAIModel.temperature_must_be_valid(0.5) == 0.5


@patch("openai.ChatCompletion.create")
@patch.object(FileItem, "get_content", return_value="content")
def test_get_result_for_item(mock_get_content, mock_create):
    mock_create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content="content"))])
    model = OpenAIModel(prompts=["prompt"])
    result, messages = model.get_result_for_item(
        FileItem(path="path", content="content", key="key")
    )
    assert result == "content"
    assert messages[-1]["content"] == "content"


@patch("openai.ChatCompletion.create")
@patch.object(FileItem, "get_content", return_value="content")
def test_get_result_with_validation(mock_get_content, mock_create):
    mock_create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content="content"))])
    model = OpenAIModel(prompts=["prompt"])
    result, messages = model.get_result_with_validation(
        FileItem(path="path", content="content", key="key"),
        [{"role": "assistant", "content": "previous content"}],
        [ValidationResult(message="error message", level="error", validator="validator")],
    )
    assert result == "content"
    assert messages[-1]["content"] == "content"


@patch.object(FileItem, "get_content", return_value="content")
def test_replace_sentinel_values(mock_get_content):
    model = OpenAIModel(prompts=["<<FILE_PATH>> <<FILE_CONTENT>>"])
    replaced = model._replace_sentinel_values(
        "<<FILE_PATH>> <<FILE_CONTENT>>", FileItem(path="path", content="content", key="key")
    )
    assert replaced == "key content"


def test_extract_code_from_completion():
    model = OpenAIModel(prompts=["prompt"])
    assert model._extract_code_from_completion("```\ncode\n```") == "code"
    assert model._extract_code_from_completion("code") == "code"
