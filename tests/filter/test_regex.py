# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Tests for the RegexFilter component."""

from autotransform.filter.regex import FileContentRegexFilter, RegexFilter

from .filter_test import run_filter_tests


def test_regex():
    """Runs simple tests on the Regex filter
    """
    filt = RegexFilter({"pattern": "foo"})
    test_cases = {
        "foo.py": True,
        "bar/foo.py": True,
        "bar/foo": True,
        "bar/baz": False,
        "baz": False,
        "oof": False,
    }
    run_filter_tests(filt, test_cases)

def test_inverted_regex():
    """Runs simple tests on the Regex filter
    """
    filt = RegexFilter({"pattern": "foo"}).invert()
    test_cases = {
        "foo.py": False,
        "bar/foo.py": False,
        "bar/foo": False,
        "bar/baz": True,
        "baz": True,
        "oof": True,
    }
    run_filter_tests(filt, test_cases)

def test_file_content_regex(tmpdir):
    """Runs simple tests on the Regex filter
    """
    filt = FileContentRegexFilter({"pattern": "foo"})
    test_file_dir = tmpdir.mkdir("non_empty_dir")
    test_file_1 = test_file_dir.join("test1.txt")
    test_file_1.write("foo")
    test_file_2 = test_file_dir.join("foo.txt")
    test_file_2.write("bar")
    test_cases = {
        str(test_file_1): True,
        str(test_file_2): False,
    }
    run_filter_tests(filt, test_cases)

def test_inverted_file_content_regex(tmpdir):
    """Runs simple tests on the Regex filter
    """
    filt = FileContentRegexFilter({"pattern": "foo"}).invert()
    test_file_dir = tmpdir.mkdir("non_empty_dir")
    test_file_1 = test_file_dir.join("test1.txt")
    test_file_1.write("foo")
    test_file_2 = test_file_dir.join("foo.txt")
    test_file_2.write("bar")
    test_cases = {
        str(test_file_1): False,
        str(test_file_2): True,
    }
    run_filter_tests(filt, test_cases)
