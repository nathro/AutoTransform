# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for the GitGrepInput component."""

from autotransform.input.gitgrep import GitGrepInput


def test_pattern_present() -> None:
    """Tests running git grep when a known match is present."""

    inp = GitGrepInput({"pattern": "Tests for the GitGrepInput component."})
    found_files = inp.get_items()
    assert len(found_files) is 1, "Only one file match expected."
    test_file = __file__.lower().replace("\\", "/")
    assert found_files[0].get_path().lower() == test_file, "The test file should be found."


def test_pattern_not_present() -> None:
    """Tests running git grep when no match is present."""

    inp = GitGrepInput({"pattern": "foobar" + "fizzbuzz" + "barfoo" + "buzzfizz" + "notpresent"})
    found_files = inp.get_items()
    assert len(found_files) == 0, "No matches should be found"
