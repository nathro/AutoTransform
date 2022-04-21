# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""A class used to test Transformer components."""

import pathlib

import mock

from autotransform.item.file import FileItem
from autotransform.transformer.base import Transformer


class TransformerTester:
    """A utility class used to test Transformers. Follows a .input and .output
    file pattern for running tests.

    Attributes:
        path (str): The path the transformer should test from.
        transformer (Transformer): The transformer being tested.
    """

    path: str
    transformer: Transformer

    def __init__(self, path: str, transformer: Transformer):
        parent_dir = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/")
        self.path = parent_dir + "/data/" + path
        self.transformer = transformer

    def check(self):
        """Checks that the provided Transformer writes expected output by checking the results
        of running the Transformer against the .input file against the .output file."""

        # pylint: disable="unspecified-encoding"

        with open(self.path + ".input", "r") as input_file:
            input_content = input_file.read()
        with open(self.path + ".output", "r") as output_file:
            output_content = output_file.read()

        mock_file = mock.create_autospec(FileItem)
        mock_file.get_content.return_value = input_content
        self.transformer.transform(
            {"items": [mock_file], "metadata": {"title": "Foo", "summary": "Bar", "tests": "Baz"}}
        )
        mock_file.write_content.assert_called_once_with(output_content)

    def update(self):
        """Updates the expected output of a Transformer by running it and writing the results to
        the .output file."""

        # pylint: disable="unspecified-encoding"

        with open(self.path + ".input", "r") as input_file:
            input_content = input_file.read()

        mock_file = mock.create_autospec(FileItem)
        mock_file.get_content.return_value = input_content
        self.transformer.transform(
            {"items": [mock_file], "metadata": {"title": "Foo", "summary": "Bar", "tests": "Baz"}}
        )
        output_content = [
            args[0] for name, args, _ in mock_file.mock_calls if name == "write_content"
        ][0]
        with open(self.path + ".output", "w") as output_file:
            output_file.write(output_content)
