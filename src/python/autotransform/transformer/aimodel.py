# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the AIModelTransformer."""

from __future__ import annotations

from time import sleep
from typing import Any, ClassVar, Dict, List, Type

from autotransform.batcher.base import Batch
from autotransform.command.base import FACTORY as command_factory
from autotransform.command.base import Command
from autotransform.event.handler import EventHandler
from autotransform.event.verbose import VerboseEvent
from autotransform.item.base import Item
from autotransform.item.file import FileItem
from autotransform.model.base import FACTORY as model_factory
from autotransform.model.base import Model
from autotransform.transformer.base import TransformerName
from autotransform.transformer.single import SingleTransformer
from autotransform.validator.base import FACTORY as validator_factory
from autotransform.validator.base import ValidationResultLevel, Validator
from pydantic import Field, validator


class AIModelTransformer(SingleTransformer):
    """A transformer which uses AI models to perform a completion to generate code.

    Attributes:
        model (Model): The AI Model to use for completions.
        commands (optional, List[Command]): A set of commands to use on transformed files
            before validation. Useful for correcting things like formatting. Defaults to an
            empty list.
        max_completion_attempts (optional, int): The maximum number of times to try the Model.
            Defaults to 3.
        max_validation_attempts (optional, int): The maximum number of times to validate
            results. Defaults to 3.
        validators (optional, List[Validator]): A set of validators to use to provide feedback to
            the Model with issues it may have produced. Defaults to an empty list.
        name (ClassVar[TransformerName]): The name of the component.
    """

    model: Model
    commands: List[Command] = Field(default_factory=list)
    max_completion_attempts: int = 3
    max_validation_attempts: int = 3
    validators: List[Validator] = Field(default_factory=list)

    name: ClassVar[TransformerName] = TransformerName.AI_MODEL

    @validator("max_completion_attempts")
    @classmethod
    def max_completion_attempts_must_be_positive(cls, v: int) -> int:
        """Validates the max_completion_attempts is a positive number.

        Args:
            v (int): The maximum number of completion attempts for the Model.

        Raises:
            ValueError: Raises an error when the max_completion_attempts is not positive.

        Returns:
            int: The unmodified max_completion_attempts.
        """

        if v < 1:
            raise ValueError("The max completion attempts must be at least 1")
        return v

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

    def _transform_item(self, item: Item) -> None:
        """Replaces a file with the result from an AI Model.

        Args:
            item (Item): The file that will be transformed.
        """

        assert isinstance(item, FileItem)

        event_handler = EventHandler.get()
        original_content = item.get_content()
        batch: Batch = {"title": "test", "items": [item]}

        for i in range(self.max_completion_attempts):
            try:
                result, result_data = self.model.get_result_for_item(item)
            except Exception as e:  # pylint: disable=broad-exception-caught
                result = None
                sleep(min(4 ** (i + 1), 60))
                event_handler.handle(
                    VerboseEvent({"message": f"Model Failure on {item.get_path()}: {e}"}),
                )

        completion_success = False
        for _ in range(self.max_validation_attempts):
            if result is None:
                item.write_content(original_content)
                return

            # Update File
            item.write_content(result)

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
                    failures.append(validation_result)

            # Check if another completion is required
            completion_success = not failures
            if completion_success:
                break

            for i in range(self.max_completion_attempts):
                try:
                    result, result_data = self.model.get_result_with_validation(
                        item,
                        result_data,
                        failures,
                    )
                except Exception as e:  # pylint: disable=broad-exception-caught
                    result = None
                    sleep(min(4 ** (i + 1), 60))
                    event_handler.handle(
                        VerboseEvent({"message": f"Model Failure on {item.get_path()}: {e}"}),
                    )

        # If we had validation failures on our last run, just use the original content
        if not completion_success:
            event_handler.handle(
                VerboseEvent({"message": "Completion failed, using original content"})
            )
            item.write_content(original_content)

    @classmethod
    def from_data(cls: Type[AIModelTransformer], data: Dict[str, Any]) -> AIModelTransformer:
        """Produces an instance of the component from decoded data.

        Args:
            data (Mapping[str, Any]): The JSON decoded data.

        Returns:
            AIModelTransformer: An instance of the component.
        """

        model = model_factory.get_instance(data["model"])
        commands = [command_factory.get_instance(c) for c in data.get("commands", [])]
        max_completion_attempts = data.get("max_completion_attempts", 3)
        max_validation_attempts = data.get("max_validation_attempts", 3)
        validators = [validator_factory.get_instance(v) for v in data.get("validators", [])]

        return cls(
            model=model,
            commands=commands,
            max_completion_attempts=max_completion_attempts,
            max_validation_attempts=max_validation_attempts,
            validators=validators,
        )
