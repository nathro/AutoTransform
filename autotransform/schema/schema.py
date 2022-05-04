# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The heart of AutoTransform, AutoTransformSchemas represent all information
required to fully execute a change.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Mapping, Optional

import autotransform.schema
from autotransform.batcher.base import Batch, Batcher
from autotransform.batcher.factory import BatcherFactory
from autotransform.change.base import Change
from autotransform.command.base import Command
from autotransform.command.factory import CommandFactory
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.filter.base import Filter
from autotransform.filter.factory import FilterFactory
from autotransform.input.base import Input
from autotransform.input.factory import InputFactory
from autotransform.item.base import Item
from autotransform.repo.base import Repo
from autotransform.repo.factory import RepoFactory
from autotransform.schema.config import SchemaConfig
from autotransform.transformer.base import Transformer
from autotransform.transformer.factory import TransformerFactory
from autotransform.validator.base import ValidationError, Validator
from autotransform.validator.factory import ValidatorFactory


class AutoTransformSchema:
    """The heart of AutoTransform, pulls together all components required to execute
    a transformation.

    Attributes:
        _input (Input): The Input which gets Items.
        _batcher (Batcher): The Batcher which batches filtered Items in to logical groups.
        _transformer (Transformer): The Transformer which actually modifies files.
        _filters (List[Filter]): A list of Filters to apply to Items.
        _validators (List[Validator]): A list of Validators to ensure the changes
            did not break anything.
        _commands (List[Command]): A list of Commands that run post-processing on
            the changes.
        _repo (Optional[Repo]): A Repo to control submission of changes to version
            control or code review systems.
        _config (SchemaConfig): Any configuration needed by the schema so that it can run.
    """

    # pylint: disable=too-many-instance-attributes

    _input: Input
    _batcher: Batcher
    _transformer: Transformer
    _config: SchemaConfig

    _filters: List[Filter]
    _validators: List[Validator]
    _commands: List[Command]
    _repo: Optional[Repo]

    def __init__(
        self,
        inp: Input,
        batcher: Batcher,
        transformer: Transformer,
        config: SchemaConfig,
        filters: List[Filter] = None,
        validators: List[Validator] = None,
        commands: List[Command] = None,
        repo: Optional[Repo] = None,
    ):
        """A simple constructor.

        Args:
            inp (Input): The Schema's Input.
            batcher (Batcher): The Schema's Batcher.
            transformer (Transformer): The Schema's Transformer.
            config (SchemaConfig, optional): The Schema's Config.
            filters (List[Filter], optional): The Schema's Filters. Defaults to None which is
                converted in to an empty list.
            validators (List[Validator], optional): The Schema's Validators. Defaults to None which
                is converted in to an empty list.
            commands (List[Command], optional): The Schema's Commands. Defaults to None which is
                converted in to an empty list.
            repo (Optional[Repo], optional): The Schema's Repo. Defaults to None.
        """

        # pylint: disable=too-many-arguments

        self._input = inp
        self._batcher = batcher
        self._transformer = transformer
        self._config = config

        self._filters = filters if isinstance(filters, List) else []
        self._validators = validators if isinstance(validators, List) else []
        self._commands = commands if isinstance(commands, List) else []
        self._repo = repo

    def get_input(self) -> Input:
        """Gets the Input object of the Schema.

        Returns:
            Input: The Input object of the Schema.
        """

        return self._input

    def get_batcher(self) -> Batcher:
        """Gets the Batcher object of the Schema.

        Returns:
            Batcher: The Batcher object of the Schema.
        """

        return self._batcher

    def get_transformer(self) -> Transformer:
        """Gets the Transformer object of the Schema.

        Returns:
            Transformer: The Transformer object of the Schema.
        """

        return self._transformer

    def get_config(self) -> SchemaConfig:
        """Gets the configuration of the Schema.

        Returns:
            SchemaConfig: The configuration of the Schema.
        """

        return self._config

    def get_filters(self) -> List[Filter]:
        """Gets the Filter objects of the Schema.

        Returns:
            List[Filter]: The Filter objects of the Schema.
        """

        return self._filters

    def get_validators(self) -> List[Validator]:
        """Gets the Validator objects of the Schema.

        Returns:
            List[Validator]: The Validator objects of the Schema.
        """

        return self._validators

    def get_commands(self) -> List[Command]:
        """Gets the Command objects of the Schema.

        Returns:
            List[Command]: The Command objects of the Schema.
        """

        return self._commands

    def get_repo(self) -> Optional[Repo]:
        """Gets the repo object of the Schema.

        Returns:
            Optional[Repo]: The Repo object of the Schema.
        """

        return self._repo

    def add_filter(self, filt: Filter) -> None:
        """Adds a filter to the list of filters for the Schema.

        Args:
            filt (Filter): The filter to add.
        """

        self._filters.append(filt)

    def get_batches(self) -> List[Batch]:
        """Runs the Input to get eligible Items, filters them, then batches them.
        Note: this function is not thread safe.

        Returns:
            List[Batch]: The Batches for the change
        """

        autotransform.schema.current = self
        event_handler = EventHandler.get()
        event_handler.handle(DebugEvent({"message": "Begin get_batches"}))

        # Get Items
        event_handler.handle(DebugEvent({"message": "Begin get_items"}))
        all_items = self._input.get_items()
        event_handler.handle(
            DebugEvent({"message": f"Items: {json.dumps([item.bundle() for item in all_items])}"})
        )

        # Filter Items
        event_handler.handle(DebugEvent({"message": "Begin filters"}))
        valid_items: List[Item] = []
        for item in all_items:
            is_valid = True
            for cur_filter in self._filters:
                if not cur_filter.is_valid(item):
                    is_valid = False
                    type_str = "".join([w.capitalize() for w in cur_filter.get_type().split("_")])
                    event = DebugEvent(
                        {"message": f"[{type_str}] Invalid Item: {json.dumps(item.bundle())}"}
                    )
                    event_handler.handle(event)
                    break
            if is_valid:
                valid_items.append(item)
        event_handler.handle(
            DebugEvent(
                {"message": f"Valid items: {json.dumps([item.bundle() for item in valid_items])}"}
            )
        )

        # Batch Items
        event_handler.handle(DebugEvent({"message": "Begin batching"}))
        batches = self._batcher.batch(valid_items)
        encodable_batches = [
            {"items": [item.bundle() for item in batch["items"]], "metadata": batch["metadata"]}
            for batch in batches
        ]
        event_handler.handle(DebugEvent({"message": f"Batches: {json.dumps(encodable_batches)}"}))
        autotransform.schema.current = None

        return batches

    def execute_batch(self, batch: Batch, change: Optional[Change] = None) -> None:
        """Executes changes for a batch, including setting up the Repo, running the Transformer,
        checking all Validators, running Commands, submitting changes if present, and rewinding
        the Repo if changes are submitted. Note: this function is not thread safe.

        Args:
            batch (Batch): The Batch to execute.
            change (Optional[Change]): An associated Change that is being updated.

        Raises:
            ValidationError: If one of the Schema's Validators fails raises an exception.
        """

        autotransform.schema.current = self
        event_handler = EventHandler.get()
        encodable_batch = {
            "items": [item.bundle() for item in batch["items"]],
            "metadata": batch["metadata"],
        }
        event_handler.handle(
            DebugEvent({"message": f"Begin execute_batch: {json.dumps(encodable_batch)}"})
        )

        # Make sure repo is clean before executing
        repo = self._repo
        if repo is not None:
            event_handler.handle(DebugEvent({"message": "Clean repo"}))
            repo.clean(batch)

        # Execute transformation
        self._transformer.transform(batch)

        # Run pre-validation commands
        pre_validation_commands = [
            command for command in self._commands if command.get_should_run_pre_validation()
        ]
        for command in pre_validation_commands:
            event_handler.handle(DebugEvent({"message": f"Running command {command.get_type()}"}))
            command.run(batch)

        # Validate the changes
        for validator in self._validators:
            validation_result = validator.validate(batch)
            event_handler.handle(
                DebugEvent(
                    {
                        "message": f"[{validation_result['validator']}] Validation Result: "
                        + validation_result["level"].name
                    }
                )
            )

            if validation_result["level"].value > self._config.get_allowed_validation_level().value:
                event_handler.handle(
                    DebugEvent({"message": f"[{validation_result['validator']}] Validation Failed"})
                )
                raise ValidationError(validation_result)

        # Run post-validation commands
        post_validation_commands = [
            command for command in self._commands if not command.get_should_run_pre_validation()
        ]
        for command in post_validation_commands:
            event_handler.handle(DebugEvent({"message": f"Running command {command.get_type()}"}))
            command.run(batch)

        # Handle repo state, submitting changes if present and reseting the repo
        if repo is not None:
            event_handler.handle(DebugEvent({"message": "Checking for changes"}))
            if repo.has_changes(batch):
                event_handler.handle(DebugEvent({"message": "Changes found"}))
                event_handler.handle(DebugEvent({"message": "Submitting changes"}))
                repo.submit(batch, change=change)
                event_handler.handle(DebugEvent({"message": "Rewinding repo"}))
                repo.rewind(batch)
            else:
                if change is not None:
                    event_handler.handle(
                        DebugEvent(
                            {
                                "message": f"Abandoning Change ({str(change)}) "
                                + "due to no changes in update."
                            }
                        )
                    )
                    change.abandon()
                event_handler.handle(DebugEvent({"message": "No changes found"}))
        event_handler.handle(DebugEvent({"message": "Finish batch"}))
        autotransform.schema.current = None

    def run(self):
        """Fully run a given Schema including getting and executing all Batches.
        Note: this function is not thread safe."""

        autotransform.schema.current = self
        batches = self.get_batches()
        for batch in batches:
            self.execute_batch(batch)
        autotransform.schema.current = None

    def bundle(self) -> Dict[str, Any]:
        """Bundles the Schema in to a format that can be JSON encoded.

        Returns:
            Dict[str, Any]: The bundled data of the Schema.
        """

        bundle = {
            "input": self._input.bundle(),
            "batcher": self._batcher.bundle(),
            "transformer": self._transformer.bundle(),
            "filters": [f.bundle() for f in self._filters],
            "validators": [validator.bundle() for validator in self._validators],
            "commands": [command.bundle() for command in self._commands],
            "config": self._config.bundle(),
        }
        repo = self._repo
        if isinstance(repo, Repo):
            bundle["repo"] = repo.bundle()
        return bundle

    def to_json(self, pretty: bool = False) -> str:
        """Converts the Schema in to JSON that can be passed and stored.

        Args:
            pretty (bool, optional): Forces the JSON to be human readable. Defaults to False.

        Returns:
            str: The JSON representing the Schema
        """

        bundle = self.bundle()
        if pretty:
            return json.dumps(bundle, indent=4)
        return json.dumps(bundle)

    @staticmethod
    def from_json(json_bundle: str) -> AutoTransformSchema:
        """Produces a Schema from supplied JSON

        Args:
            json_bundle (str): A JSON encoded bundle representing a Schema

        Returns:
            AutoTransformSchema: The Schema represented by the JSON
        """

        return AutoTransformSchema.from_bundle(json.loads(json_bundle))

    @staticmethod
    def from_bundle(bundle: Mapping[str, Any]) -> AutoTransformSchema:
        """Takes a bundle of information from a source like JSON and produces the associated Schema.

        Args:
            bundle (Mapping[str, Any]): The bundle representing the Schema.

        Returns:
            AutoTransformSchema: The Schema represented by the bundle.
        """

        inp = InputFactory.get(bundle["input"])
        batcher = BatcherFactory.get(bundle["batcher"])
        transformer = TransformerFactory.get(bundle["transformer"])
        config = SchemaConfig.from_data(bundle["config"])

        filters = [FilterFactory.get(f) for f in bundle["filters"]]
        validators = [ValidatorFactory.get(validator) for validator in bundle["validators"]]
        commands = [CommandFactory.get(command) for command in bundle["commands"]]

        if "repo" in bundle:
            repo = RepoFactory.get(bundle["repo"])
        else:
            repo = None

        return AutoTransformSchema(
            inp,
            batcher,
            transformer,
            filters=filters,
            validators=validators,
            commands=commands,
            repo=repo,
            config=config,
        )
