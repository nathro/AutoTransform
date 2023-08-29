# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the OpenAIModel."""

from typing import Any, ClassVar, Dict, List, Optional, Sequence, Tuple

import openai  # pylint: disable=import-error
from autotransform.config import get_config
from autotransform.event.handler import EventHandler
from autotransform.event.verbose import VerboseEvent
from autotransform.item.file import FileItem
from autotransform.model.base import Model, ModelName
from autotransform.validator.base import ValidationResult
from pydantic import validator  # pylint: disable=import-error


class OpenAIModel(Model[List[Dict[str, str]]]):
    """The base for Model components. Used by AutoTransform to interact with AI models
    such as LLMs.

    Attributes:
        prompt (str): The prompt to use for completition. Uses sentry values to replace
            values in the prompt.
            <<FILE_PATH>> - Replaced with the path of the file being transformed.
            <<FILE_CONTENT>> - Replaced with the content of the file being transformed.
        model_name (optional, str): The model to use for completition. Defaults to gpt-3.5-turbo.
        system_message (optional, Optional[str]): The system message to use. Defaults to None.
        temperature (optional, float): The temperature to use to control the quality of outputs.
            Defaults to 0.4.
        name (ClassVar[ModelName]): The name of the Component.
    """

    prompt: str
    model_name: str = "gpt-3.5-turbo"
    system_message: Optional[str] = None
    temperature: float = 0.4

    name: ClassVar[ModelName] = ModelName.OPEN_AI

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

    def get_result_for_item(self, item: FileItem) -> Tuple[str, List[Dict[str, str]]]:
        """Gets a completion for a FileItem, usually used to find new file content.

        Args:
            item (FileItem): The FileItem to get the result for.

        Returns:
            Tuple[str, List[Dict[str, str]]]: The result for the Item along with previous
                messages.
        """

        if openai.api_key is None:
            openai.api_key = get_config().open_ai_api_key

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

        chat_completion = openai.ChatCompletion.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature,
        )
        completion_result = chat_completion.choices[0].message.content
        messages.append({"role": "assistant", "content": completion_result})

        self._log_info(item, chat_completion)
        return (self._extract_code_from_completion(completion_result), messages)

    def get_result_with_validation(
        self,
        item: FileItem,
        result_data: List[Dict[str, str]],
        validation_failures: Sequence[ValidationResult],
    ) -> Tuple[str, List[Dict[str, str]]]:
        """Gets a new result based on ValidationResult issues.

        Args:
            item (FileItem): The FileItem to get the result for.
            result_data (List[Dict[str, str]]): The previously returned result data.
            validation_failures (Sequence[ValidationResult]): The validation failures.

        Returns:
            Tuple[str, TResultData]: The result for the failures along with any information needed
                for future completions.
        """

        failures = [str(validation_result.message) for validation_result in validation_failures]
        failure_message = "\n".join(failures)
        result_data.append(
            {
                "role": "user",
                "content": f"The following errors were found\n{failure_message}\n\n"
                + "Provide the file with fixes for these errors.",
            },
        )

        chat_completion = openai.ChatCompletion.create(
            model=self.model_name,
            messages=result_data,
            temperature=self.temperature,
        )

        completion_result = chat_completion.choices[0].message.content
        result_data.append({"role": "assistant", "content": completion_result})

        self._log_info(item, chat_completion)
        return (self._extract_code_from_completion(completion_result), result_data)

    def _replace_sentinel_values(self, prompt: str, item: FileItem) -> str:
        """Replaces sentinel values in a prompt.

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

    def _log_info(self, item: FileItem, chat_completion: Any) -> None:
        """Logs information about a completion.

        Args:
            item (FileItem): The FileItem that is having the completion done for it.
            chat_completion (Any): The chat completion.
        """

        event_handler = EventHandler.get()

        token_usage = (
            f"Tokens Used\nPrompt: {chat_completion.usage.prompt_tokens}\n"
            + f"Completition: {chat_completion.usage.completion_tokens}"
        )
        event_handler.handle(VerboseEvent({"message": token_usage}))
        completition_result = chat_completion.choices[0].message.content
        message = f"The completion result for {item.get_path()}:\n\n{completition_result}"
        event_handler.handle(VerboseEvent({"message": message}))
