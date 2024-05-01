# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the OpenAIModel."""

from typing import ClassVar, List, Optional, Sequence, Tuple

import anthropic
from autotransform.config import get_config
from autotransform.event.handler import EventHandler
from autotransform.event.model import AIModelCompletionEvent
from autotransform.item.file import FileItem
from autotransform.model.base import Model, ModelName
from autotransform.validator.base import ValidationResult
from pydantic import validator  # pylint: disable=import-error


class AnthropicAIModel(Model[str]):
    """The base for Model components. Used by AutoTransform to interact with AI models
    such as LLMs.

    Attributes:
        prompts (List[str]): The prompts to use for completition. Only the response from the last
            prompt in the list will be used for code extraction. Previous prompts can be leveraged
            to provide a path for the model to produce better results, i.e. for test generation.
            Uses sentry values to replace values in the prompt.
                <<FILE_PATH>> - Replaced with the path of the file being transformed.
                <<FILE_CONTENT>> - Replaced with the content of the file being transformed.
        max_tokens_to_sample(optional, int): The maximum tokens to use in the completion.
            Defaults to 4096.
        model_name (optional, str): The model to use for completition. Defaults to gpt-3.5-turbo.
        system_message (optional, Optional[str]): The system message to use. Defaults to None.
        name (ClassVar[ModelName]): The name of the Component.
    """

    prompts: List[str]
    max_tokens_to_sample: int = 4096
    model_name: str = "claude-instant-1"
    system_message: Optional[str] = None

    name: ClassVar[ModelName] = ModelName.OPEN_AI

    @validator("prompts")
    @classmethod
    def prompts_must_contain_at_least_one_item(cls, v: List[str]) -> List[str]:
        """Validates there is at least one prompt in the list.

        Args:
            v (List[str]): The prompts to send to the model.

        Raises:
            ValueError: Raises an error when the prompts contains no items.

        Returns:
            int: The unmodified temperature.
        """

        if not v:
            raise ValueError("At least one prompt must be included in the list")
        return v

    @validator("max_tokens_to_sample")
    @classmethod
    def max_tokens_to_sample_must_be_valid(cls, v: int) -> int:
        """Validates that max tokens is between 1 and 100,000.

        Args:
            v (int): The maximum number of tokens to sample for the result.

        Raises:
            ValueError: Raises an error when the maximum tokens is invalid.

        Returns:
            int: The unmodified max_tokens_to_sample.
        """

        if v < 1:
            raise ValueError("Max tokens to sample must be positive")
        if v > 100000:
            raise ValueError("Max tokens can not be greater than 100,000")
        return v

    def get_result_for_item(self, _item: FileItem) -> Tuple[str, str]:
        """Gets a completion for a FileItem, usually used to find new file content.

        Args:
            item (FileItem): The FileItem to get the result for.

        Returns:
            Tuple[str, str]: The result for the Item along with full prompt for follow-ups.
        """

        client = anthropic.Anthropic(api_key=get_config().anthropic_api_key)

        # Set up prompt
        current_prompt = self.system_message or ""
        current_prompt = (
            "Code should be contained within <code></code> tags. "
            + "Explanations should be contained within <explanation></explanation> tags. "
            + current_prompt
        )
        for prompt in self.prompts:
            current_prompt = (
                f"{current_prompt}{anthropic.HUMAN_PROMPT}{prompt}{anthropic.AI_PROMPT}"
            )
            completion = client.completions.create(
                model=self.model_name,
                max_tokens_to_sample=self.max_tokens_to_sample,
                prompt=current_prompt,
            )
            completion_result = completion.completion

            EventHandler.get().handle(
                AIModelCompletionEvent(
                    {
                        "input_tokens": client.count_tokens(current_prompt),
                        "output_tokens": client.count_tokens(completion_result),
                        "completion": completion_result,
                    }
                )
            )

            current_prompt = f"{current_prompt}{completion_result}"

        return (self._extract_code_from_completion(completion_result), current_prompt)

    def get_result_with_validation(
        self,
        _item: FileItem,
        result_data: str,
        validation_failures: Sequence[ValidationResult],
    ) -> Tuple[str, str]:
        """Gets a new result based on ValidationResult issues.

        Args:
            item (FileItem): The FileItem to get the result for.
            result_data (str): The previously returned result data.
            validation_failures (Sequence[ValidationResult]): The validation failures.

        Returns:
            Tuple[str, str]: The result for the failures along with any information needed
                for future completions.
        """

        current_prompt = result_data
        failure_message = "\n".join(
            str(validation_result.message) for validation_result in validation_failures
        )
        failure_message = (
            f"The following errors were found\n{failure_message}\n\n"
            + "Provide the file with fixes for these errors."
        )
        current_prompt = (
            f"{current_prompt}{anthropic.HUMAN_PROMPT}{failure_message}"
            + anthropic.AI_PROMPT
        )

        client = anthropic.Anthropic(api_key=get_config().anthropic_api_key)
        completion = client.completions.create(
            model=self.model_name,
            prompt=current_prompt,
            max_tokens_to_sample=self.max_tokens_to_sample,
        )

        completion_result = completion.completion

        EventHandler.get().handle(
            AIModelCompletionEvent(
                {
                    "input_tokens": client.count_tokens(current_prompt),
                    "output_tokens": client.count_tokens(completion_result),
                    "completion": completion_result,
                }
            )
        )

        current_prompt = f"{current_prompt}{completion_result}"
        return (self._extract_code_from_completion(completion_result), current_prompt)

    def _replace_sentinel_values(self, prompt: str, item: FileItem) -> str:
        """Replaces sentinel values in a prompt.

        Args:
            prompt (str): The prompt with potential sentinel values to replace.
            item (FileItem): The Item to use for replacing sentinel values.

        Returns:
            str: The prompt with sentinel values replaced.
        """
        return prompt.replace("<<FILE_PATH>>", item.get_path()).replace(
            "<<FILE_CONTENT>>", f"<code>\n{item.get_content()}\n</code>"
        )

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
            if line.strip() == "<code>":
                in_code = True
                continue
            if line.strip() == "</code>":
                break
            if in_code:
                code_lines.append(line)
        return "\n".join(code_lines)
