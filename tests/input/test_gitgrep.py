# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Tests for the GitGrepInput component."""

from autotransform.inputsource.gitgrep import GitGrepInput


def test_pattern_present() -> None:
    """Tests running git grep when a known match is present."""

    inp = GitGrepInput({"pattern": "Tests for the GitGrepInput component."})
    found_files = inp.get_files()
    assert len(found_files) is 1, "Only one file match expected."
    test_file = __file__.lower().replace("\\", "/")
    assert found_files[0].lower() == test_file, "The test file should be found."


def test_pattern_not_present() -> None:
    """Tests running git grep when no match is present"""

    inp = GitGrepInput({"pattern": "foobar" + "fizzbuzz" + "barfoo" + "buzzfizz" + "notpresent"})
    found_files = inp.get_files()
    assert len(found_files) is 0, "No matches should be found"
