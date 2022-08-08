# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Test for the LibCSTTransformer component."""

from autotransform.transformer.libcst import LibCSTTransformer

from .transformer_tester import TransformerTester


def test_noop():
    """A simple check that the libcst executes as expected when noop."""

    tester = TransformerTester(
        "libcst/noop",
        LibCSTTransformer(
            command_module="libcst.codemod.commands.convert_format_to_fstring",
            command_name="ConvertFormatStringCommand",
        ),
    )
    tester.check()


def test_format_spec():
    """A simple check that the libcst executes as expected with changes."""

    tester = TransformerTester(
        "libcst/format_spec",
        LibCSTTransformer(
            command_module="libcst.codemod.commands.convert_format_to_fstring",
            command_name="ConvertFormatStringCommand",
        ),
    )
    tester.check()
