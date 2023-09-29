# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from argparse import ArgumentParser
from unittest.mock import patch, mock_open
from autotransform.scripts.migrations import p1_0_5


def test_get_arg_parser():
    parser = p1_0_5.get_arg_parser()
    assert isinstance(parser, ArgumentParser)
    assert parser.description == "Upgrade Manager JSON files for 1.0.0 -> 1.0.1"
    assert parser.prog == "AutoTransform"
    assert "--path" in parser.format_help()


@patch("argparse.ArgumentParser.parse_args")
@patch("autotransform.scripts.migrations.p1_0_5.update_manager_data")
@patch("autotransform.scripts.migrations.p1_0_5.Manager")
@patch("builtins.open", new_callable=mock_open, read_data='{"steps": []}')
def test_main(mock_open, mock_manager, mock_update, mock_args):
    mock_args.return_value.path = "test.json"
    p1_0_5.main()
    mock_open.assert_called_once_with("test.json", "r", encoding="UTF-8")
    mock_update.assert_called_once()
    assert mock_manager.from_data.called
    assert mock_manager.from_data.return_value.write.called


@patch("autotransform.scripts.migrations.p1_0_5.update_step_data")
def test_update_manager_data(mock_update_step):
    manager_data = {"steps": [{}]}
    p1_0_5.update_manager_data(manager_data)
    mock_update_step.assert_called_once()


@patch("autotransform.scripts.migrations.p1_0_5.update_condition_data")
def test_update_step_data(mock_update_condition):
    step_data = {"name": "conditional", "condition": {}}
    p1_0_5.update_step_data(step_data)
    mock_update_condition.assert_called_once()


def test_update_condition_data(capsys):
    condition_data = {"name": p1_0_5.ConditionName.CHANGE_STATE, "value": "approved"}
    p1_0_5.update_condition_data(condition_data)
    assert condition_data["name"] == p1_0_5.ConditionName.REVIEW_STATE

    condition_data = {"name": p1_0_5.ConditionName.CHANGE_STATE, "value": ["approved"]}
    p1_0_5.update_condition_data(condition_data)
    assert "Can not migrate in/not_in comparisons for conditions" in capsys.readouterr().out
