# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from __future__ import annotations

import json
from typing import Any, Dict, List, Mapping, Optional

from autotransform.batcher.base import Batcher, BatchWithFiles
from autotransform.batcher.factory import BatcherFactory
from autotransform.command.base import Command
from autotransform.command.factory import CommandFactory
from autotransform.common.cachedfile import CachedFile
from autotransform.filter.base import Filter
from autotransform.filter.factory import FilterFactory
from autotransform.inputsource.base import Input
from autotransform.inputsource.factory import InputFactory
from autotransform.repo.base import Repo
from autotransform.repo.factory import RepoFactory
from autotransform.transformer.base import Transformer
from autotransform.transformer.factory import TransformerFactory
from autotransform.validator.base import ValidationError, ValidationResultLevel, Validator
from autotransform.validator.factory import ValidatorFactory


class PackageConfiguration:
    allowed_validation_level: ValidationResultLevel

    def __init__(
        self, allowed_validation_level: ValidationResultLevel = ValidationResultLevel.NONE
    ):
        self.allowed_validation_level = allowed_validation_level

    def bundle(self):
        return {
            "allowed_validation_level": self.allowed_validation_level,
        }

    @classmethod
    def from_data(cls, data: Dict[str, Any]) -> PackageConfiguration:
        if "allowed_validation_level" in data:
            validation_level = data["allowed_validation_level"]
            if not ValidationResultLevel.has_value(validation_level):
                validation_level = ValidationResultLevel.from_name(validation_level)
        else:
            validation_level = ValidationResultLevel.NONE
        return cls(validation_level)


class AutoTransformPackage:
    # pylint: disable=too-many-instance-attributes

    inputsource: Input
    batcher: Batcher
    transformer: Transformer

    filters: List[Filter]
    validators: List[Validator]
    commands: List[Command]
    repo: Optional[Repo]

    config: PackageConfiguration

    def __init__(
        self,
        inp: Input,
        batcher: Batcher,
        transformer: Transformer,
        filters: List[Filter] = None,
        validators: List[Validator] = None,
        commands: List[Command] = None,
        repo: Optional[Repo] = None,
        config: PackageConfiguration = PackageConfiguration(),
    ):
        # pylint: disable=too-many-arguments

        self.inputsource = inp
        self.batcher = batcher
        self.transformer = transformer

        self.filters = filters if isinstance(filters, List) else []
        self.validators = validators if isinstance(validators, List) else []
        self.commands = commands if isinstance(commands, List) else []
        self.repo = repo

        self.config = config

    def get_batches(self) -> List[BatchWithFiles]:
        valid_files = []
        for file in self.inputsource.get_files():
            cached_file = CachedFile(file)
            is_valid = True
            for cur_filter in self.filters:
                if not cur_filter.is_valid(cached_file):
                    is_valid = False
                    break
            if is_valid:
                valid_files.append(cached_file)
        batches = self.batcher.batch(valid_files)
        return [
            {"files": [valid_files[file] for file in batch["files"]], "metadata": batch["metadata"]}
            for batch in batches
        ]

    def execute_batch(self, batch: BatchWithFiles) -> None:
        repo = self.repo
        if repo is not None:
            repo.clean(batch)
        for file in batch["files"]:
            self.transformer.transform(file)
        for validator in self.validators:
            validation_result = validator.validate(batch)
            if validation_result["level"] > self.config.allowed_validation_level:
                raise ValidationError(validation_result)
        for command in self.commands:
            command.run(batch)
        if repo is not None:
            if repo.has_changes(batch):
                repo.submit(batch)
                repo.rewind(batch)

    def run(self):
        batches = self.get_batches()
        for batch in batches:
            self.execute_batch(batch)

    def bundle(self) -> Dict[str, Any]:
        bundle = {
            "inputsource": self.inputsource.bundle(),
            "batcher": self.batcher.bundle(),
            "transformer": self.transformer.bundle(),
            "filters": [filter.bundle() for filter in self.filters],
            "validators": [validator.bundle() for validator in self.validators],
            "commands": [command.bundle() for command in self.commands],
            "config": self.config.bundle(),
        }
        repo = self.repo
        if isinstance(repo, Repo):
            bundle["repo"] = repo.bundle()
        return bundle

    def to_json(self, pretty: bool = False) -> str:
        bundle = self.bundle()
        if pretty:
            return json.dumps(bundle, indent=4)
        return json.dumps(bundle)

    @staticmethod
    def from_json(json_bundle: str) -> AutoTransformPackage:
        return AutoTransformPackage.from_bundle(json.loads(json_bundle))

    @staticmethod
    def from_bundle(bundle: Mapping[str, Any]) -> AutoTransformPackage:
        inp = InputFactory.get(bundle["inputsource"])
        batcher = BatcherFactory.get(bundle["batcher"])
        transformer = TransformerFactory.get(bundle["transformer"])

        filters = [FilterFactory.get(filter) for filter in bundle["filters"]]
        validators = [ValidatorFactory.get(validator) for validator in bundle["validators"]]
        commands = [CommandFactory.get(command) for command in bundle["commands"]]

        if "repo" in bundle:
            repo = RepoFactory.get(bundle["repo"])
        else:
            repo = None

        config = PackageConfiguration.from_data(bundle["config"])

        return AutoTransformPackage(
            inp,
            batcher,
            transformer,
            filters=filters,
            validators=validators,
            commands=commands,
            repo=repo,
            config=config,
        )
