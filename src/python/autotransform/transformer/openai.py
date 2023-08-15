# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the OpenAITransformer."""

from __future__ import annotations

from typing import ClassVar, Optional

import openai  # pylint: disable=import-error
from autotransform.item.base import Item
from autotransform.item.file import FileItem
from autotransform.transformer.base import TransformerName
from autotransform.transformer.single import SingleTransformer


class OpenAITransformer(SingleTransformer):
    """A transformer which uses OpenAI models to perform a completion to generate code.

    Attributes:
        prompt (str): The prompt to use for completition. Uses sentry values to replace
            values in the prompt.
            <<FILE_PATH>> - Replaced with the path of the file being transformed.
            <<FILE_CONTENT>> - Replaced with the content of the file being transformed.
        model (optional, str): The model to use for completition. Defaults to gpt-3.5-turbo.
        system_message (optional, Optional[str]): The system message to use. Defaults to None.
        temperature (optional, float): The temperature to use to control the quality of outputs.
            Defaults to 0.4.
        name (ClassVar[TransformerName]): The name of the component.
    """

    prompt: str
    model: str = "gpt-3.5-turbo"
    system_message: Optional[str] = None
    temperature: float = 0.4

    name: ClassVar[TransformerName] = TransformerName.OPEN_AI

    def _transform_item(self, item: Item) -> None:
        """Replaces all instances of a pattern in the file with the replacement string.

        Args:
            item (Item): The file that will be transformed.
        """

        # pylint: disable=unspecified-encoding

        assert isinstance(item, FileItem)
        messages = []
        # Set up messages for prompt
        if self.system_message:
            messages.append({"role": "system", "content": self.system_message})
        # Replace sentinel values in prompt
        prompt = self.prompt.replace("<<FILE_PATH>>", item.get_path())
        prompt = prompt.replace("<<FILE_CONTENT>>", item.get_content())
        messages.append({"role": "user", "content": prompt})
        # Get completition
        chat_completion = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature
        )
        result = chat_completion.choices[0].message.content
        code_lines = []
        in_code = False
        # Try to extract from formatted code
        for line in result.split("\n"):
            if line.startswith("```"):
                if in_code:
                    break
                in_code = True
                continue
            if in_code:
                code_lines.append(line)
        # If we hit this, that means the completition didn't use formatting
        if not in_code:
            code = result
        else:
            code = "\n".join(code_lines)
        item.write_content(code)
