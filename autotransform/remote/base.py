# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The base class and associated classes for Remote components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, Mapping, TypedDict, TypeVar

from autotransform.remote.type import RemoteType
from autotransform.schema.schema import AutoTransformSchema

TParams = TypeVar("TParams", bound=Mapping[str, Any])


class RemoteBundle(TypedDict):
    """A bundled version of the Remote object used for JSON encoding."""

    params: Mapping[str, Any]
    type: RemoteType


class Remote(Generic[TParams], ABC):
    """The base for Remote components.

    Attributes:
        params (TParams): The paramaters that control operation of the Remote.
            Should be defined using a TypedDict in subclasses
    """

    params: TParams

    def __init__(self, params: TParams):
        """A simple constructor.

        Args:
            params (TParams): The paramaters used to set up the Remote
        """
        self.params = params

    @abstractmethod
    def get_type(self) -> RemoteType:
        """Used to map Remote components 1:1 with an enum, allowing construction from JSON.

        Returns:
            RemoteType: The unique type associated with this Remote
        """

    @abstractmethod
    def run(self, schema: AutoTransformSchema) -> str:
        """Triggers a remote run of the schema.

        Args:
            schema (AutoTransformSchema): The schema to schedule a remote run for
        Returns:
            str: A string representation of the remote run that can be used to monitor status
        """

    def bundle(self) -> RemoteBundle:
        """Generates a JSON encodable bundle.
        If a component's params are not JSON encodable this method should be overridden to provide
        an encodable version.

        Returns:
            RemoteBundle: The encodable bundle
        """
        return {
            "params": self.params,
            "type": self.get_type(),
        }

    @staticmethod
    @abstractmethod
    def from_data(data: Mapping[str, Any]) -> Remote:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle

        Returns:
            Remote: An instance of the Remote
        """
