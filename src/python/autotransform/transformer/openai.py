# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the OpenAITransformer."""

from __future__ import annotations

from typing import Any, ClassVar, Dict, List, Optional, Type

import openai  # pylint: disable=import-error
from autotransform.batcher.base import Batch
from autotransform.config import get_config
from autotransform.event.handler import EventHandler
from autotransform.event.verbose import VerboseEvent
from autotransform.item.base import Item
from autotransform.item.file import FileItem
from autotransform.transformer.base import TransformerName
from autotransform.transformer.single import SingleTransformer
from autotransform.validator.base import FACTORY as validator_factory
from autotransform.validator.base import ValidationResultLevel, Validator
from pydantic import Field


class OpenAITransformer(SingleTransformer):
    """A transformer which uses OpenAI models to perform a completion to generate code.

    Attributes:
        prompt (str): The prompt to use for completion. Uses sentry values to replace
            values in the prompt.
            <<FILE_PATH>> - Replaced with the path of the file being transformed.
            <<FILE_CONTENT>> - Replaced with the content of the file being transformed.
        max_validator_attempts (optional, float): The maximum number of times to run validators.
            Defaults to 3.
        model (optional, str): The model to use for completion. Defaults to gpt-3.5-turbo.
        system_message (optional, Optional[str]): The system message to use. Defaults to None.
        temperature (optional, float): The temperature to use to control the quality of outputs.
            Defaults to 0.4.
        validators (optional, List[Validator]): A set of validators to use to provide feedback to
            the LLM with issues it may have produced. Defaults to an empty list.
        name (ClassVar[TransformerName]): The name of the component.
    """

    prompt: str
    max_validator_attempts: int = 3
    model: str = "gpt-3.5-turbo"
    system_message: Optional[str] = None
    temperature: float = 0.4
    validators: List[Validator] = Field(default_factory=list)

    name: ClassVar[TransformerName] = TransformerName.OPEN_AI

    def _transform_item(self, item: Item) -> None:
        """Replaces a file with the completion results from an OpenAI completion.

        Args:
            item (Item): The file that will be transformed.
        """

        if openai.api_key is None:
            openai.api_key = get_config().open_ai_api_key

        assert isinstance(item, FileItem)
        messages = []
        # Set up messages for prompt
        if self.system_message:
            messages.append({"role": "system", "content": self.system_message})
        messages.append(
            {
                "role": "user",
                "content": self._replace_sentinel_values(self.prompt, item),
            }
        )
        # Get completion
        chat_completion = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )
        completion_result = chat_completion.choices[0].message.content
        EventHandler.get().handle(
            VerboseEvent({"message": f"The completion result\n\n{completion_result}"})
        )
        item.write_content(self._extract_code_from_completion(completion_result))
        run_validators = bool(self.validators)
        try_count = 0
        batch: Batch = {"title": "test", "items": [item]}
        while run_validators and try_count < self.max_validator_attempts:
            try_count += 1
            failures = []
            for validator in self.validators:
                validation_result = validator.check(batch, None)
                if validation_result.level != ValidationResultLevel.NONE:
                    failures.append(str(validation_result.message))
            run_validators = bool(failures)
            if failures:
                messages.append({"role": "assistant", "content": completion_result})
                failure_message = "\n".join(failures)
                messages.append(
                    {
                        "role": "user",
                        "content": f"The following errors were found\n{failure_message}"
                        + "provide the file with fixes for these errors.",
                    },
                )
                chat_completion = openai.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                )
                completion_result = chat_completion.choices[0].message.content
                EventHandler.get().handle(
                    VerboseEvent({"message": f"The completion result\n\n{completion_result}"})
                )
                item.write_content(self._extract_code_from_completion(completion_result))

    def _replace_sentinel_values(self, prompt: str, item: FileItem) -> str:
        """Replaces sentinel values in a prompt

        Args:
            prompt (str): The prompt with potential sentinel values to replace.
            item (FileItem): The Item to use for replacing sentinel values.

        Returns:
            str: The prompt with sentinel values replaced.
        """
        new_prompt = prompt.replace("<<FILE_PATH>>", item.get_path())
        return new_prompt.replace("<<FILE_CONTENT>>", item.get_content())

    def _extract_code_from_completion(self, result: str) -> str:
        """Extracts code from the result of an OpenAI completion.

        Args:
            result (str): The completion result.

        Returns:
            str: The extracted code from the completion result.
        """

        code_lines = []
        in_code = False
        # Checks for code inside formatting blocks
        for line in result.split("\n"):
            if line.startswith("```"):
                if in_code:
                    break
                in_code = True
                continue
            if in_code:
                code_lines.append(line)
        # Hit when no formatting is present or only trailing backticks
        if not in_code or not code_lines:
            code = result.removesuffix("```")
        else:
            code = "\n".join(code_lines)
        return code

    @classmethod
    def from_data(cls: Type[OpenAITransformer], data: Dict[str, Any]) -> OpenAITransformer:
        """Produces an instance of the component from decoded data.

        Args:
            data (Mapping[str, Any]): The JSON decoded data.

        Returns:
            OpenAITransformer: An instance of the component.
        """

        prompt = data["prompt"]
        assert isinstance(prompt, str)
        model = data.get("model", "gpt-3.5-turbo")
        system_message = data.get("system_message")
        temperature = data.get("temperature", 0.4)
        validators = [
            validator_factory.get_instance(validator) for validator in data.get("validators", [])
        ]

        return cls(
            prompt=prompt,
            model=model,
            system_message=system_message,
            temperature=temperature,
            validators=validators,
        )
