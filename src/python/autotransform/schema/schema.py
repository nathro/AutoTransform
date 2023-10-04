# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The heart of AutoTransform, AutoTransformSchemas represent all information
required to fully execute a change."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import autotransform.schema
from autotransform.batcher.base import FACTORY as batcher_factory
from autotransform.batcher.base import Batch, Batcher
from autotransform.change.base import Change
from autotransform.command.base import FACTORY as command_factory
from autotransform.command.base import Command
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.event.verbose import VerboseEvent
from autotransform.filter.base import FACTORY as filter_factory
from autotransform.filter.base import BulkFilter, Filter
from autotransform.input.base import FACTORY as input_factory
from autotransform.input.base import Input
from autotransform.item.base import Item
from autotransform.repo.base import FACTORY as repo_factory
from autotransform.repo.base import Repo
from autotransform.schema.config import SchemaConfig
from autotransform.transformer.base import FACTORY as transformer_factory
from autotransform.transformer.base import Transformer
from autotransform.util.component import ComponentModel
from autotransform.util.console import choose_options_from_list, choose_yes_or_no
from autotransform.validator.base import FACTORY as validator_factory
from autotransform.validator.base import ValidationError, Validator
from pydantic import Field


class AutoTransformSchema(ComponentModel):
    """The heart of AutoTransform, pulls together all components required to execute
    a transformation.

    Attributes:
        input (Input): The Input which gets Items.
        batcher (Batcher): The Batcher which batches filtered Items in to logical groups.
        transformer (Transformer): The Transformer which actually modifies files.
        config (SchemaConfig): Any configuration needed by the schema so that it can run.
        filters (List[Filter], optional): A list of Filters to apply to Items. Defaults to [].
        validators (List[Validator], optional): A list of Validators to ensure the changes
            did not break anything. Defaults to [].
        commands (List[Command], optional): A list of Commands that run post-processing on
            the changes. Defaults to [].
        repo (Optional[Repo], optional): A Repo to control submission of changes to version
            control or code review systems. Defaults to None.
    """

    # pylint: disable=too-many-instance-attributes

    input: Input
    batcher: Batcher
    transformer: Transformer
    config: SchemaConfig

    filters: List[Filter] = Field(default_factory=list)
    validators: List[Validator] = Field(default_factory=list)
    commands: List[Command] = Field(default_factory=list)
    repo: Optional[Repo] = None

    def get_items(self) -> List[Item]:
        """Runs the Input to get eligible Items and filters them.
        Note: this function is not thread safe.

        Returns:
            List[Item]: The valid Items for the Schema.
        """

        autotransform.schema.current = self
        event_handler = EventHandler.get()

        # Get Items
        event_handler.handle(VerboseEvent({"message": "Begin get_items"}))
        all_items = self.input.get_items()
        item_str = "\n".join([f"{item!r}," for item in all_items])
        event_handler.handle(VerboseEvent({"message": f"Num Items: {len(all_items)}"}))
        event_handler.handle(DebugEvent({"message": f"Items: [\n{item_str}\n]"}))

        # Filter Items
        event_handler.handle(VerboseEvent({"message": "Begin filters"}))
        valid_items: List[Item] = []
        for filt in self.filters:
            if isinstance(filt, BulkFilter):
                filt.pre_process(all_items)
        for item in all_items:
            is_valid = True
            for cur_filter in self.filters:
                if not cur_filter.is_valid(item):
                    is_valid = False
                    event = DebugEvent({"message": f"[{cur_filter}] Invalid Item: {item!r}"})
                    event_handler.handle(event)
                    break
            if is_valid:
                valid_items.append(item)
        if valid_items:
            valid_item_str = "\n".join([f"{item!r}," for item in valid_items])
            event_handler.handle(VerboseEvent({"message": f"Num Valid Items: {len(valid_items)}"}))
            event_handler.handle(DebugEvent({"message": f"Valid items: [\n{valid_item_str}\n]"}))
        else:
            event_handler.handle(VerboseEvent({"message": "No valid items."}))

        autotransform.schema.current = None
        return valid_items

    def get_batches(self, items: List[Item]) -> List[Batch]:
        """Runs the Input to get eligible Items, filters them, then batches them.
        Note: this function is not thread safe.

        Args:
            items (List[Item]): The Items to batch.

        Returns:
            List[Batch]: The Batches for the change
        """

        autotransform.schema.current = self
        event_handler = EventHandler.get()
        event_handler.handle(VerboseEvent({"message": "Begin get_batches"}))

        # Batch Items
        event_handler.handle(VerboseEvent({"message": "Begin batching"}))
        batches = self.batcher.batch(items)
        encodable_batches = [
            {"items": [item.bundle() for item in batch["items"]], "metadata": batch["metadata"]}
            for batch in batches
        ]
        event_handler.handle(VerboseEvent({"message": f"Num Batches: {len(batches)}"}))
        event_handler.handle(DebugEvent({"message": f"Batches: {json.dumps(encodable_batches)}"}))
        autotransform.schema.current = None

        return batches

    def execute_batch(self, batch: Batch, change: Optional[Change] = None) -> bool:
        """Executes changes for a batch, including setting up the Repo, running the Transformer,
        checking all Validators, running Commands, submitting changes if present, and rewinding
        the Repo if changes are submitted. Note: this function is not thread safe.

        Args:
            batch (Batch): The Batch to execute.
            change (Optional[Change]): An associated Change that is being updated.

        Raises:
            ValidationError: If one of the Schema's Validators fails raises an exception.

        Returns:
            bool: Whether the batch triggered a submission.
        """

        autotransform.schema.current = self
        event_handler = EventHandler.get()
        encodable_batch = {
            "items": [item.bundle() for item in batch["items"]],
            "metadata": batch["metadata"],
        }
        event_handler.handle(
            VerboseEvent(
                {"message": f"Handling Batch: {batch['title']} with {len(batch['items'])} items"}
            )
        )
        event_handler.handle(DebugEvent({"message": f"Full Batch: {json.dumps(encodable_batch)}"}))

        # Make sure repo is clean before executing
        if self.repo is not None:
            event_handler.handle(VerboseEvent({"message": "Clean repo"}))
            self.repo.rewind(batch)
            if change is None and self.repo.has_outstanding_change(batch):
                event_handler.handle(
                    VerboseEvent({"message": "Skipping batch with outstanding change"})
                )
                return False

        # Execute transformation
        result = self.transformer.transform(batch)

        # Run pre-validation commands
        pre_validation_commands = [
            command for command in self.commands if command.run_pre_validation
        ]
        for command in pre_validation_commands:
            event_handler.handle(VerboseEvent({"message": f"Running command {command}"}))
            command.run(batch, result)

        # Validate the changes
        for validator in self.validators:
            validation_result = validator.check(batch, result)
            event_handler.handle(
                VerboseEvent({"message": f"Validation Result: {validation_result}"})
            )

            if validation_result.level > self.config.allowed_validation_level:
                event_handler.handle(VerboseEvent({"message": "Validation Failed"}))
                raise ValidationError(issue=validation_result, message=validation_result.message)

        # Run post-validation commands
        post_validation_commands = [
            command for command in self.commands if not command.run_pre_validation
        ]
        for command in post_validation_commands:
            event_handler.handle(VerboseEvent({"message": f"Running command {command}"}))
            command.run(batch, result)

        submitted = False
        # Handle repo state, submitting changes if present and reseting the repo
        if self.repo is not None:
            event_handler.handle(VerboseEvent({"message": "Checking for changes"}))
            if self.repo.has_changes(batch):
                event_handler.handle(VerboseEvent({"message": "Changes found"}))
                event_handler.handle(VerboseEvent({"message": "Submitting changes"}))
                self.repo.submit(batch, result, change=change)
                event_handler.handle(VerboseEvent({"message": "Rewinding repo"}))
                self.repo.rewind(batch)
                submitted = True
            else:
                if change is not None:
                    event_handler.handle(
                        VerboseEvent({"message": "No changes in update, abandoning"})
                    )

                    change.abandon()
                event_handler.handle(VerboseEvent({"message": "No changes found"}))
        event_handler.handle(VerboseEvent({"message": "Finish batch"}))
        autotransform.schema.current = None
        return submitted

    def run(self):
        """Fully run a given Schema including getting and executing all Batches.
        Note: this function is not thread safe."""

        autotransform.schema.current = self
        items = self.get_items()
        batches = self.get_batches(items)
        num_submissions = 0
        for batch in batches:
            if (
                self.config.max_submissions is not None
                and num_submissions >= self.config.max_submissions
            ):
                EventHandler.get().handle(
                    VerboseEvent({"message": f"Max submissions reached: {num_submissions}"})
                )
                break
            if self.execute_batch(batch):
                num_submissions += 1
        autotransform.schema.current = None

    @staticmethod
    def from_data(data: Dict[str, Any]) -> AutoTransformSchema:
        """Takes data from a source like JSON and produces the associated Schema.

        Args:
            data (Dict[str, Any]): The data representing the Schema.

        Returns:
            AutoTransformSchema: The Schema represented by the data.
        """

        inp = input_factory.get_instance(data["input"])
        batcher = batcher_factory.get_instance(data["batcher"])
        transformer = transformer_factory.get_instance(data["transformer"])
        config = SchemaConfig.parse_obj(data["config"])

        filters = [filter_factory.get_instance(f) for f in data.get("filters", [])]
        validators = [
            validator_factory.get_instance(validator) for validator in data.get("validators", [])
        ]
        commands = [command_factory.get_instance(command) for command in data.get("commands", [])]

        repo = repo_factory.get_instance(data["repo"]) if "repo" in data else None

        return AutoTransformSchema(
            input=inp,
            batcher=batcher,
            transformer=transformer,
            filters=filters,
            validators=validators,
            commands=commands,
            repo=repo,
            config=config,
        )

    # pylint: disable=too-many-branches
    @staticmethod
    def from_console(prev_schema: Optional[AutoTransformSchema] = None) -> AutoTransformSchema:
        """Gets a AutoTransformSchema using console inputs.

        Args:
            prev_schema (Optional[AutoTransformSchema], optional): A previously input
                AutoTransformSchema. Defaults to None.

        Returns:
            AutoTransformSchema: The input AutoTransformSchema.
        """

        # Get Config
        config = SchemaConfig.from_console(prev_schema.config if prev_schema is not None else None)

        # Get Input
        args: Dict[str, Any] = {"allow_none": False}
        if prev_schema is not None:
            args["previous_value"] = prev_schema.input
        inp = input_factory.from_console("input", **args)
        assert inp is not None

        # Get Filters
        if prev_schema is not None and prev_schema.filters:
            filters = choose_options_from_list(
                "Choose filters to keep",
                [(filt, f"{filt!r}") for filt in prev_schema.filters],
                min_choices=0,
                max_choices=len(prev_schema.filters),
            )
        else:
            filters = []
        while choose_yes_or_no("Would you like to add a filter?"):
            filt = filter_factory.from_console("filter", allow_none=False)
            assert filt is not None
            filters.append(filt)

        # Get Batcher
        args = {"allow_none": False}
        if prev_schema is not None:
            args["previous_value"] = prev_schema.batcher
        batcher = batcher_factory.from_console("batcher", **args)
        assert batcher is not None

        # Get Transformer
        args = {"allow_none": False}
        if prev_schema is not None:
            args["previous_value"] = prev_schema.transformer
        transformer = transformer_factory.from_console("transformer", **args)
        assert transformer is not None

        # Get Validators
        if prev_schema is not None and prev_schema.validators:
            validators = choose_options_from_list(
                "Choose validators to keep",
                [(validator, f"{validator!r}") for validator in prev_schema.validators],
                min_choices=0,
                max_choices=len(prev_schema.validators),
            )
        else:
            validators = []
        while choose_yes_or_no("Would you like to add a validator?"):
            validator = validator_factory.from_console("validator", allow_none=False)
            assert validator is not None
            validators.append(validator)

        # Get Commands
        if prev_schema is not None and prev_schema.commands:
            commands = choose_options_from_list(
                "Choose commands to keep",
                [(command, f"{command!r}") for command in prev_schema.commands],
                min_choices=0,
                max_choices=len(prev_schema.commands),
            )
        else:
            commands = []
        while choose_yes_or_no("Would you like to add a command?"):
            command = command_factory.from_console("command", allow_none=False)
            assert command is not None
            commands.append(command)

        # Get Repo
        args = {"allow_none": False}
        if prev_schema is not None:
            args["previous_value"] = prev_schema.repo
        repo = repo_factory.from_console("repo", **args)
        assert repo is not None

        return AutoTransformSchema(
            input=inp,
            batcher=batcher,
            transformer=transformer,
            config=config,
            filters=filters,
            validators=validators,
            commands=commands,
            repo=repo,
        )
