# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from autotransform.batcher.base import Batcher
from autotransform.batcher.factory import BatcherFactory
from autotransform.command.base import Command
from autotransform.command.factory import CommandFactory
from autotransform.common.cachedfile import CachedFile
from autotransform.filter.base import Filter
from autotransform.filter.factory import FilterFactory
from autotransform.input.base import Input
from autotransform.input.factory import InputFactory
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

    input: Input
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

        self.input = inp
        self.batcher = batcher
        self.transformer = transformer

        self.filters = filters if isinstance(filters, List) else []
        self.validators = validators if isinstance(validators, List) else []
        self.commands = commands if isinstance(commands, List) else []
        self.repo = repo

        self.config = config

    def run(self):
        valid_files = []
        for file in self.input.get_files():
            cached_file = CachedFile(file)
            is_valid = True
            for cur_filter in self.filters:
                if not cur_filter.is_valid(cached_file):
                    is_valid = False
                    break
            if is_valid:
                valid_files.append(cached_file)
        batches = self.batcher.batch(valid_files)
        batches = [
            {"files": [valid_files[file] for file in batch["files"]], "metadata": batch["metadata"]}
            for batch in batches
        ]
        repo = self.repo
        for batch in batches:
            if repo is not None:
                self.repo.clean(batch)
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

    def to_json(self, pretty: bool = False) -> str:
        package = {
            "input": self.input.bundle(),
            "batcher": self.batcher.bundle(),
            "transformer": self.transformer.bundle(),
            "filters": [filter.bundle() for filter in self.filters],
            "validators": [validator.bundle() for validator in self.validators],
            "commands": [command.bundle() for command in self.commands],
            "config": self.config.bundle(),
        }
        repo = self.repo
        if isinstance(repo, Repo):
            package["repo"] = repo.bundle()
        if pretty:
            return json.dumps(package, indent=4)
        return json.dumps(package)

    @staticmethod
    def from_json(json_package: str) -> AutoTransformPackage:
        package = json.loads(json_package)

        inp = InputFactory.get(package["input"])
        batcher = BatcherFactory.get(package["batcher"])
        transformer = TransformerFactory.get(package["transformer"])

        filters = [FilterFactory.get(filter) for filter in package["filters"]]
        validators = [ValidatorFactory.get(validator) for validator in package["validators"]]
        commands = [CommandFactory.get(command) for command in package["commands"]]

        if "repo" in package:
            repo = RepoFactory.get(package["repo"])
        else:
            repo = None

        config = PackageConfiguration.from_data(package["config"])

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
