# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the OpenAITransformer."""

from __future__ import annotations

from time import sleep
from typing import Any, ClassVar, Dict, List, Optional, Type

import openai  # pylint: disable=import-error
from autotransform.batcher.base import Batch
from autotransform.command.base import FACTORY as command_factory
from autotransform.command.base import Command
from autotransform.config import get_config
from autotransform.event.handler import EventHandler
from autotransform.event.verbose import VerboseEvent
from autotransform.item.base import Item
from autotransform.item.file import FileItem
from autotransform.transformer.base import TransformerName
from autotransform.transformer.single import SingleTransformer
from autotransform.validator.base import FACTORY as validator_factory
from autotransform.validator.base import ValidationResultLevel, Validator
from pydantic import Field, validator


class OpenAITransformer(SingleTransformer):
    """A transformer which uses OpenAI models to perform a completion to generate code.

    Attributes:
        prompt (str): The prompt to use for completition. Uses sentry values to replace
            values in the prompt.
            <<FILE_PATH>> - Replaced with the path of the file being transformed.
            <<FILE_CONTENT>> - Replaced with the content of the file being transformed.
        commands (optional, List[Command]): A set of commands to use on transformed files
            before validation. Useful for correcting things like formatting. Defaults to an
            empty list.
        max_completion_attempts (optional, int): The maximum number of times to try the OpenAI
            API. Defaults to 3.
        max_validation_attempts (optional, int): The maximum number of times to validate
            completitions. Defaults to 3.
        model (optional, str): The model to use for completition. Defaults to gpt-3.5-turbo.
        system_message (optional, Optional[str]): The system message to use. Defaults to None.
        temperature (optional, float): The temperature to use to control the quality of outputs.
            Defaults to 0.4.
        validators (optional, List[Validator]): A set of validators to use to provide feedback to
            the LLM with issues it may have produced. Defaults to an empty list.
        name (ClassVar[TransformerName]): The name of the component.
    """

    prompt: str
    commands: List[Command] = Field(default_factory=list)
    max_completion_attempts: int = 3
    max_validation_attempts: int = 3
    model: str = "gpt-3.5-turbo"
    system_message: Optional[str] = None
    temperature: float = 0.4
    validators: List[Validator] = Field(default_factory=list)

    name: ClassVar[TransformerName] = TransformerName.OPEN_AI

    # pylint: disable=invalid-name
    @validator("max_completion_attempts")
    @classmethod
    def max_completion_attempts_must_be_positive(cls, v: int) -> int:
        """Validates the max_completion_attempts is a positive number.

        Args:
            v (int): The maximum number of completion attempts for the OpenAI API.

        Raises:
            ValueError: Raises an error when the max_completion_attempts is not positive.

        Returns:
            int: The unmodified max_completion_attempts.
        """

        if v < 1:
            raise ValueError("The max completion attempts must be at least 1")
        return v

    # pylint: disable=invalid-name
    @validator("max_validation_attempts")
    @classmethod
    def max_validation_attempts_must_be_positive(cls, v: int) -> int:
        """Validates the max_validation_attempts is a positive number.

        Args:
            v (int): The maximum number of validation attempts for completion.

        Raises:
            ValueError: Raises an error when the max_validation_attempts is not positive.

        Returns:
            int: The unmodified max_validation_attempts.
        """

        if v < 1:
            raise ValueError("The max validation attempts must be at least 1")
        return v

    # pylint: disable=invalid-name
    @validator("temperature")
    @classmethod
    def temperature_must_be_valid(cls, v: float) -> float:
        """Validates the temperature is between 0 and 1.

        Args:
            v (float): The temperature to use for model completion.

        Raises:
            ValueError: Raises an error when the temperature is not in the valid range.

        Returns:
            int: The unmodified temperature.
        """

        if v >= 1.0 or v <= 0.0:
            raise ValueError("The temperature must be between 0.0 and 1.0")
        return v

    def _transform_item(self, item: Item) -> None:
        """Replaces a file with the completition results from an OpenAI completition.

        Args:
            item (Item): The file that will be transformed.
        """

        if openai.api_key is None:
            openai.api_key = get_config().open_ai_api_key

        assert isinstance(item, FileItem)

        event_handler = EventHandler.get()
        original_content = item.get_content()
        batch: Batch = {"title": "test", "items": [item]}

        # Set up messages for prompt
        messages = []
        if self.system_message:
            messages.append({"role": "system", "content": self.system_message})
        messages.append(
            {
                "role": "user",
                "content": self._replace_sentinel_values(self.prompt, item),
            }
        )

        completion_success = False
        for _ in range(self.max_validation_attempts):
            # Get completion
            chat_completion = None
            for i in range(self.max_completion_attempts):
                try:
                    chat_completion = openai.ChatCompletion.create(
                        model=self.model,
                        messages=messages,
                        temperature=self.temperature,
                    )
                    break
                except Exception as e:  # pylint: disable=broad-exception-caught
                    chat_completion = None
                    sleep(min(4 ** (i+1), 60))
                    event_handler.handle(
                        VerboseEvent({"message": f"API Failure on {item.get_path()}: {e}"}),
                    )

            if chat_completion is None:
                item.write_content(original_content)
                return

            # Log completion information
            token_usage = (
                f"Prompt: {chat_completion.usage.prompt_tokens}"
                + f" - Completition: {chat_completion.usage.completion_tokens}"
            )
            event_handler.handle(VerboseEvent({"message": token_usage}))
            completition_result = chat_completion.choices[0].message.content
            message = f"The completion result for {item.get_path()}:\n\n{completition_result}"
            event_handler.handle(VerboseEvent({"message": message}))

            # Update File
            item.write_content(self._extract_code_from_completion(completition_result))

            # Run commands to fix file
            for command in self.commands:
                try:
                    command.run(batch, None)
                except Exception:  # pylint: disable=broad-exception-caught
                    event_handler.handle(
                        VerboseEvent({"message": f"Failed to run command {command}"})
                    )

            # Run validators to identify issues with completion
            failures = []
            for completion_validator in self.validators:
                validation_result = completion_validator.check(batch, None)
                if validation_result.level != ValidationResultLevel.NONE:
                    failures.append(str(validation_result.message))

            # Check if another completion is required
            completion_success = not failures
            if completion_success:
                break

            # Add messages for handling failures for next completion
            messages.append({"role": "assistant", "content": completition_result})
            failure_message = "\n".join(failures)
            messages.append(
                {
                    "role": "user",
                    "content": f"The following errors were found\n{failure_message}"
                    + "provide the file with fixes for these errors.",
                },
            )

        # If we had validation failures on our last run, just use the original content
        if not completion_success:
            event_handler.handle(
                VerboseEvent({"message": "Completion failed, using original content"})
            )
            item.write_content(original_content)

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
        """Extracts code from the result of an OpenAI completition.

        Args:
            result (str): The completition result.

        Returns:
            str: The extracted code from the completition result.
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
        commands = [command_factory.get_instance(c) for c in data.get("commands", [])]
        model = data.get("model", "gpt-3.5-turbo")
        system_message = data.get("system_message", None)
        temperature = data.get("temperature", 0.4)
        validators = [validator_factory.get_instance(v) for v in data.get("validators", [])]

        return cls(
            prompt=prompt,
            commands=commands,
            model=model,
            system_message=system_message,
            temperature=temperature,
            validators=validators,
        )
