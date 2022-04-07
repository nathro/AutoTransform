# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The base class and associated classes for SchemaBuilders."""

from abc import ABC, abstractmethod
from typing import List, Optional

from autotransform.batcher.base import Batcher
from autotransform.batcher.single import SingleBatcher
from autotransform.command.base import Command
from autotransform.filter.base import Filter
from autotransform.inputsource.base import Input
from autotransform.repo.base import Repo
from autotransform.schema.config import Config
from autotransform.schema.schema import AutoTransformSchema
from autotransform.transformer.base import Transformer
from autotransform.validator.base import Validator


class SchemaBuilder(ABC):
    """The base for SchemaBuilders. SchemaBuilders are used for programatic schema generation.
    This can be used in conjunction with inputsource params or configuration to customize Schemas run
    through automation. Can also be used to generate JSON schemas that can be utilized.
    """

    @abstractmethod
    def get_inputsource(self) -> Input:
        """Get the Input for the schema.

        Returns:
            Input: The Input that will be used in the built schema
        """

    def get_filters(self) -> List[Filter]:
        """Get the Filters for the schema.

        Returns:
            List[Filter]: The Filters that will be used in the built schema
        """

        # pylint: disable=no-self-use

        return []

    def get_batcher(self) -> Batcher:
        """Get the Batcher for the schema.

        Returns:
            Batcher: The Batcher that will be used in the built schema
        """

        # pylint: disable=no-self-use

        return SingleBatcher({"metadata": {"title": ""}})

    @abstractmethod
    def get_transformer(self) -> Transformer:
        """Get the Transformer for the schema.

        Returns:
            Transformer: The Transformer that will be used in the built schema
        """

    def get_validators(self) -> List[Validator]:
        """Get the Validators for the schema.

        Returns:
            List[Validator]: The Validators that will be used in the built schema
        """

        # pylint: disable=no-self-use

        return []

    def get_commands(self) -> List[Command]:
        """Get the Commands for the schema.

        Returns:
            List[Command]: The Commands that will be used in the built schema
        """

        # pylint: disable=no-self-use

        return []

    def get_repo(self) -> Optional[Repo]:
        """Get the Repo for the schema.

        Returns:
            Repo: The Repo that will be used in the built schema
        """

        # pylint: disable=no-self-use

        return None

    def get_config(self) -> Config:
        """Get the Config for the schema.

        Returns:
            Config: The Config that will be used in the built schema
        """

        # pylint: disable=no-self-use

        return Config()

    def build(self) -> AutoTransformSchema:
        """Builds a Schema based on the state of the SchemaBuilder.

        Returns:
            AutoTransformSchema: The Schema produced by this SchemaBuilder
        """
        return AutoTransformSchema(
            self.get_inputsource(),
            self.get_batcher(),
            self.get_transformer(),
            filters=self.get_filters(),
            validators=self.get_validators(),
            commands=self.get_commands(),
            repo=self.get_repo(),
            config=self.get_config(),
        )

    def dump_to_file(self, path: str) -> None:
        """Dumps the Schema this SchemaBuilder would produce to the file located at the provided
        path.

        Args:
            path (str): The path of the file to dump the JSON encoded Schema to
        """

        # pylint: disable=unspecified-encoding

        with open(path, "w") as file:
            file.write(self.build().to_json(pretty=True))
