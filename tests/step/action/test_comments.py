# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that the comments actions works as expected."""

import pytest

from autotransform.step.action.comments import CommentAction


def test_empty_body():
    """Checks that a comment action with an empty body can not be created."""

    with pytest.raises(ValueError, match="Comment body must be non-empty"):
        CommentAction(body="")
