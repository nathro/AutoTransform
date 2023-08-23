# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for the RegexFilter and RegexFileContentFilter components."""

import pytest
from autotransform.filter.regex import RegexFileContentFilter, RegexFilter
from autotransform.item.file import FileItem


@pytest.mark.parametrize(
    "pattern, inverted, path, result",
    [
        ("(foo|fizz)", False, "foo.py", True),
        ("(foo|fizz)", False, "bar/foo.py", True),
        ("(foo|fizz)", False, "bar/foo", True),
        ("(foo|fizz)", False, "bar/baz", False),
        ("(foo|fizz)", False, "baz", False),
        ("(foo|fizz)", False, "oof", False),
        ("(foo|fizz)", False, "fizz/foo.py", True),
        ("(foo|fizz)", False, "fizz/bar.py", True),
        ("(foo|fizz)", False, "bar/fizz.py", True),
        ("(foo|fizz)", True, "foo.py", False),
        ("(foo|fizz)", True, "bar/foo.py", False),
        ("(foo|fizz)", True, "bar/foo", False),
        ("(foo|fizz)", True, "bar/baz", True),
        ("(foo|fizz)", True, "baz", True),
        ("(foo|fizz)", True, "oof", True),
        ("(foo|fizz)", True, "fizz/foo.py", False),
        ("(foo|fizz)", True, "fizz/bar.py", False),
        ("(foo|fizz)", True, "bar/fizz.py", False),
    ],
)
def test_regex(pattern, inverted, path, result):
    """Runs simple tests on the regex filter."""
    filt = RegexFilter(pattern=pattern, inverted=inverted)
    item = FileItem(key=path)
    assert filt.is_valid(item) == result


@pytest.mark.parametrize(
    "pattern, inverted, content, result",
    [
        ("(foo|fizz)", False, "foo", True),
        ("(foo|fizz)", False, "bar", False),
        ("(foo|fizz)", False, "fizz", True),
        ("(foo|fizz)", True, "foo", False),
        ("(foo|fizz)", True, "bar", True),
        ("(foo|fizz)", True, "fizz", False),
    ],
)
def test_file_content_regex(tmpdir, pattern, inverted, content, result):
    """Runs simple tests on the regex file content filter."""
    filt = RegexFileContentFilter(pattern=pattern, inverted=inverted)
    test_file_dir = tmpdir.mkdir("non_empty_dir")
    test_file = test_file_dir.join("test.txt")
    test_file.write(content)
    item = FileItem(key=str(test_file))
    assert filt.is_valid(item) == result
