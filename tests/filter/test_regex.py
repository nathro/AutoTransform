# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for the RegexFilter and RegexFileContentFilter components."""

from autotransform.filter.regex import RegexFileContentFilter, RegexFilter
from autotransform.item.file import FileItem


def test_regex():
    """Runs simple tests on the regex filter."""

    filt = RegexFilter(pattern="(foo|fizz)")
    test_cases = {
        "foo.py": True,
        "bar/foo.py": True,
        "bar/foo": True,
        "bar/baz": False,
        "baz": False,
        "oof": False,
        "fizz/foo.py": True,
        "fizz/bar.py": True,
        "bar/fizz.py": True,
    }
    test_cases = [(FileItem(key=path), result) for path, result in test_cases.items()]
    for item, result in test_cases:
        assert filt.is_valid(item) == result


def test_inverted_regex():
    """Runs simple tests on the inverted regex filter."""

    filt = RegexFilter(pattern="(foo|fizz)", inverted=True)
    test_cases = {
        "foo.py": False,
        "bar/foo.py": False,
        "bar/foo": False,
        "bar/baz": True,
        "baz": True,
        "oof": True,
        "fizz/foo.py": False,
        "fizz/bar.py": False,
        "bar/fizz.py": False,
    }
    test_cases = [(FileItem(key=path), result) for path, result in test_cases.items()]
    for item, result in test_cases:
        assert filt.is_valid(item) == result


def test_file_content_regex(tmpdir):
    """Runs simple tests on the regex file content filter."""

    filt = RegexFileContentFilter(pattern="(foo|fizz)")
    test_file_dir = tmpdir.mkdir("non_empty_dir")
    test_file_1 = test_file_dir.join("test1.txt")
    test_file_1.write("foo")
    test_file_2 = test_file_dir.join("test2.txt")
    test_file_2.write("bar")
    test_file_3 = test_file_dir.join("test3.txt")
    test_file_3.write("fizz")
    test_cases = {
        str(test_file_1): True,
        str(test_file_2): False,
        str(test_file_3): True,
    }
    test_cases = [(FileItem(key=path), result) for path, result in test_cases.items()]
    for item, result in test_cases:
        assert filt.is_valid(item) == result


def test_inverted_file_content_regex(tmpdir):
    """Runs simple tests on the inverted regex file content filter."""

    filt = RegexFileContentFilter(pattern="(foo|fizz)", inverted=True)
    test_file_dir = tmpdir.mkdir("non_empty_dir")
    test_file_1 = test_file_dir.join("test1.txt")
    test_file_1.write("foo")
    test_file_2 = test_file_dir.join("foo.txt")
    test_file_2.write("bar")
    test_file_3 = test_file_dir.join("test3.txt")
    test_file_3.write("fizz")
    test_cases = {
        str(test_file_1): False,
        str(test_file_2): True,
        str(test_file_3): False,
    }
    test_cases = [(FileItem(key=path), result) for path, result in test_cases.items()]
    for item, result in test_cases:
        assert filt.is_valid(item) == result
