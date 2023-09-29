# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from argparse import ArgumentParser
from unittest.mock import patch, MagicMock
from autotransform.scripts.commands import initialize


def test_add_args():
    parser = ArgumentParser()
    initialize.add_args(parser)
    args = parser.parse_args(["--simple", "--github"])
    assert args.simple
    assert args.github


@patch("os.path.exists")
@patch("autotransform.config.config.Config")
@patch("autotransform.scripts.commands.initialize.choose_yes_or_no")
def test_initialize_config(mock_choose, mock_config, mock_exists):
    mock_exists.return_value = False
    mock_config.from_console.return_value = (mock_config, None, None)
    mock_choose.return_value = False
    with patch(
        "autotransform.scripts.commands.initialize.Config.from_console",
        return_value=(mock_config, None, None),
    ):
        config, github, jenkins = initialize.initialize_config("path", "name")
    assert config
    assert not github
    assert not jenkins


@patch("os.path.exists")
@patch("autotransform.config.config.Config")
@patch("autotransform.scripts.commands.initialize.choose_yes_or_no")
def test_initialize_config_existing_simple(mock_choose, mock_config, mock_exists):
    mock_exists.return_value = True
    mock_config.from_console.return_value = (mock_config, None, None)
    mock_choose.return_value = False
    with patch(
        "autotransform.scripts.commands.initialize.Config.from_console",
        return_value=(mock_config, None, None),
    ):
        config, github, jenkins = initialize.initialize_config("path", "name", simple=True)
    assert config
    assert not github
    assert not jenkins


@patch("os.path.exists")
@patch("autotransform.config.config.Config")
@patch("autotransform.scripts.commands.initialize.choose_yes_or_no")
def test_initialize_config_existing_not_simple(mock_choose, mock_config, mock_exists):
    mock_exists.return_value = True
    mock_config.from_console.return_value = (mock_config, None, None)
    mock_choose.return_value = False
    with patch(
        "autotransform.scripts.commands.initialize.Config.from_console",
        return_value=(mock_config, None, None),
    ):
        config, github, jenkins = initialize.initialize_config("path", "name")
    assert config
    assert not github
    assert not jenkins


@patch("os.path.exists")
@patch("autotransform.config.config.Config")
@patch("autotransform.scripts.commands.initialize.choose_yes_or_no")
def test_initialize_config_github_jenkins(mock_choose, mock_config, mock_exists):
    mock_exists.return_value = False
    mock_config.from_console.return_value = (mock_config, True, True)
    mock_choose.return_value = False
    with patch(
        "autotransform.scripts.commands.initialize.Config.from_console",
        return_value=(mock_config, True, True),
    ):
        config, github, jenkins = initialize.initialize_config(
            "path", "name", use_github=True, use_jenkins=True
        )
    assert config
    assert github
    assert jenkins


@patch("os.makedirs")
@patch("os.path.exists")
@patch("autotransform.scripts.commands.initialize.choose_yes_or_no")
def test_initialize_repo(mock_choose, mock_exists, mock_makedirs):
    mock_exists.return_value = True
    mock_choose.return_value = True
    with patch(
        "autotransform.scripts.commands.initialize.get_examples_dir", return_value="examples_dir"
    ), patch(
        "autotransform.scripts.commands.initialize.get_repo_config_dir",
        return_value="repo_config_dir",
    ), patch(
        "autotransform.scripts.commands.initialize.Manager"
    ), patch(
        "autotransform.scripts.commands.initialize.SchemaMap"
    ), patch(
        "autotransform.scripts.commands.initialize.Scheduler"
    ), patch(
        "autotransform.scripts.commands.initialize.AutoTransformSchema"
    ), patch(
        "autotransform.scripts.commands.initialize.json"
    ), patch(
        "autotransform.scripts.commands.initialize.info"
    ), patch(
        "builtins.open", new_callable=MagicMock
    ):
        initialize.initialize_repo("repo_dir", None, use_github=True, use_jenkins=True)


@patch("os.path.exists")
@patch("autotransform.scripts.commands.initialize.choose_yes_or_no")
def test_initialize_command_main_no_repo(mock_choose, mock_exists):
    mock_exists.return_value = False
    mock_choose.return_value = False
    with patch(
        "autotransform.scripts.commands.initialize.get_config_dir", return_value="config_dir"
    ), patch(
        "autotransform.scripts.commands.initialize.subprocess.check_output", side_effect=Exception
    ), patch(
        "autotransform.scripts.commands.initialize.initialize_config",
        return_value=(MagicMock(), None, None),
    ), patch(
        "autotransform.scripts.commands.initialize.info"
    ):
        initialize.initialize_command_main(MagicMock())


@patch("os.path.exists")
@patch("autotransform.scripts.commands.initialize.choose_yes_or_no")
def test_initialize_command_main_with_repo(mock_choose, mock_exists):
    mock_exists.return_value = True
    mock_choose.return_value = True
    with patch(
        "autotransform.scripts.commands.initialize.get_config_dir", return_value="config_dir"
    ), patch(
        "autotransform.scripts.commands.initialize.subprocess.check_output", return_value="repo_dir"
    ), patch(
        "autotransform.scripts.commands.initialize.initialize_config",
        return_value=(MagicMock(), None, None),
    ), patch(
        "autotransform.scripts.commands.initialize.initialize_repo"
    ), patch(
        "autotransform.scripts.commands.initialize.info"
    ):
        initialize.initialize_command_main(MagicMock())
