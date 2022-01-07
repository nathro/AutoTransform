# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from abc import ABC, abstractmethod
from typing import List, Optional

from autotransform.batcher.base import Batcher
from autotransform.batcher.single import SingleBatcher
from autotransform.command.base import Command
from autotransform.common.package import AutoTransformPackage, PackageConfiguration
from autotransform.filter.base import Filter
from autotransform.inputsource.base import Input
from autotransform.repo.base import Repo
from autotransform.transformer.base import Transformer
from autotransform.validator.base import Validator


class AutoTransformSchema(ABC):
    @abstractmethod
    def get_inputsource(self) -> Input:
        pass

    def get_filters(self) -> List[Filter]:
        # pylint: disable=no-self-use

        return []

    def get_batcher(self) -> Batcher:
        # pylint: disable=no-self-use

        return SingleBatcher({"metadata": {"title": "", "summary": None, "tests": None}})

    @abstractmethod
    def get_transformer(self) -> Transformer:
        pass

    def get_validators(self) -> List[Validator]:
        # pylint: disable=no-self-use

        return []

    def get_commands(self) -> List[Command]:
        # pylint: disable=no-self-use

        return []

    def get_repo(self) -> Optional[Repo]:
        # pylint: disable=no-self-use

        return None

    def get_config(self) -> PackageConfiguration:
        # pylint: disable=no-self-use

        return PackageConfiguration()

    def get_package(self):
        return AutoTransformPackage(
            self.get_inputsource(),
            self.get_batcher(),
            self.get_batcher(),
            filters=self.get_filters(),
            validators=self.get_validators(),
            commands=self.get_commands(),
            repo=self.get_repo(),
            config=self.get_config(),
        )

    def dump_to_file(self, path: str):
        # pylint: disable=unspecified-encoding

        with open(path, "w") as file:
            file.write(self.get_package().to_json(pretty=True))
