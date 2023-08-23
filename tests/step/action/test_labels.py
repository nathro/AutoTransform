# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that the labels actions works as expected."""

import pytest

from autotransform.step.action.labels import AddLabelsAction, RemoveLabelAction


def test_empty_label():
    """Checks that a label action with an empty label can not be created."""
    empty_label_error = "Labels must be non-empty strings"
    remove_label_error = "Label to remove must be non-empty"

    with pytest.raises(ValueError, match=empty_label_error):
        AddLabelsAction(labels=[""])

    with pytest.raises(ValueError, match=empty_label_error):
        AddLabelsAction(labels=["test", "", "foo"])

    with pytest.raises(ValueError, match=remove_label_error):
        RemoveLabelAction(label="")


def test_no_labels():
    """Checks that an AddLabelsAction with no labels can not be created."""
    no_labels_error = "At least 1 label must be provided"

    with pytest.raises(ValueError, match=no_labels_error):
        AddLabelsAction(labels=[])
