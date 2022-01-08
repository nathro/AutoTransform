# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Test for the RegexTransformer component."""

from autotransform.transformer.regex import RegexTransformer

from .transformer_tester import TransformerTester


def test_pattern_found():
    """A simple check that the regex executes as expected when found."""
    tester = TransformerTester(
        "regex/pattern_found", RegexTransformer({"pattern": "TEST", "replacement": "REP"})
    )
    tester.check()


def test_pattern_not_found():
    """A simple check that the regex does not change anything when not found."""
    tester = TransformerTester(
        "regex/pattern_not_found", RegexTransformer({"pattern": "TEST", "replacement": "REP"})
    )
    tester.check()
