# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Utilities for handling components, such as importing custom components."""

from __future__ import annotations

import importlib
import json
from abc import ABC
from dataclasses import asdict, dataclass
from enum import Enum
from functools import cached_property
from typing import Any, ClassVar, Dict, Generic, Type, TypeVar

from dacite import DaciteError, from_dict
from dacite.config import Config as DaciteConfig

from autotransform.config import fetcher as Config
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler

TComponent = TypeVar("TComponent")


class Component(ABC):
    """A base class for AutoTransform components, such as Batchers.

    Attributes:
        name (ClassVar[str]): The name of the Component.
    """

    name: ClassVar[str]

    def bundle(self) -> Dict[str, Any]:
        """Generates a JSON encodable bundle.
        If a component is not JSON encodable this method should be overridden to provide
        an encodable version.

        Returns:
            Dict[str, Any]: The encodable bundle.
        """

        def custom_asdict_factory(data):
            def convert_value(obj):
                if isinstance(obj, Enum):
                    return obj.value
                return obj

            return dict((k, convert_value(v)) for k, v in data)

        return {"name": self.name} | asdict(self, dict_factory=custom_asdict_factory)

    @classmethod
    def from_data(cls: Type[TComponent], data: Dict[str, Any]) -> TComponent:
        """Produces an instance of the component from decoded data. Override if
        the component had to be modified to encode.

        Args:
            data (Mapping[str, Any]): The JSON decoded data.

        Returns:
            TComponent: An instance of the component.
        """

        return from_dict(data_class=cls, data=data, config=DaciteConfig(cast=[Enum]))


@dataclass(frozen=True, kw_only=True)
class ComponentImport(Component):
    """The information required to import and return a component.

    Attributes:
        class_name (str): The name of the class of the component.
        module (str): The fully qualified module where the class can be imported.
    """

    class_name: str
    module: str


T = TypeVar("T", bound=Component)


class ComponentFactory(Generic[T], ABC):
    """A factory class that produces instances of components

    Attributes:
        _components (Dict[str, ComponentImport]): A mapping from a component name
            to the information needed to import and use that component.
        _custom_components (Dict[str, ComponentImport]): A mapping from a custom
            component name to the information needed to import and use that component.
        _custom_components_file (str): The name of the file containing custom component JSON.
        _type (Type[T]): The type this factory will produce.
    """

    _components: Dict[str, ComponentImport]
    _custom_components_file: str
    _type: Type[T]

    def __init__(
        self, components: Dict[str, ComponentImport], component_type: Type[T], component_file: str
    ):
        """A simple constructor

        Args:
            components (Dict[str, ComponentImport]): The library of components.
            component_type (Type[T]): The type this factory produces.
            component_file (str): The name of the file containing custom component JSON.
        """
        self._components = components
        self._custom_components_file = component_file
        self._type = component_type

    def get_components(self) -> Dict[str, ComponentImport]:
        """A simple getter for the factory's map of components.

        Returns:
            Dict[str, ComponentImport]: The components in the component library.
        """
        return self._components

    def get_custom_components(self, strict: bool = False) -> Dict[str, ComponentImport]:
        """Builds the custom components dictionary if it's not set, returns it otherwise.

        Args:
            strict (bool, optional): Whether to strictly enforce no issues arise during
                import. Defaults to False

        Returns:
            Dict[str, ComponentImport]: The custom component import info.
        """

        return self._custom_components_strict if strict else self._custom_components

    @cached_property
    def _custom_components(self) -> Dict[str, ComponentImport]:
        """A cached property for the non-strict custom components.

        Returns:
            Dict[str, ComponentImport]: Non-strict custom components.
        """

        return ComponentFactory._get_custom_components(self._custom_components_file, strict=False)

    @cached_property
    def _custom_components_strict(self) -> Dict[str, ComponentImport]:
        """A cached property for the strict custom components.

        Returns:
            Dict[str, ComponentImport]: Strict custom components.
        """

        return ComponentFactory._get_custom_components(self._custom_components_file, strict=True)

    def get_instance(self, data: Dict[str, Any]) -> T:
        """Simple method to get an instance from a bundle.

        Args:
            data (Dict[str, Any]): The bundled component.

        Returns:
            T: An instance of the associated component.
        """

        return self.get_class(data["name"]).from_data(data)

    def get_class(self, component_name: str) -> Type[T]:
        """Gets the class for a component with the specified type, usually an enum value.

        Args:
            component_name (str): The type of the component, usually an enum value. If a custom
                component is used, the type should start with custom/.

        Raises:
            ValueError: If the component could not be found.

        Returns:
            Type[T]: The class for the component.
        """

        component_info = self.get_components().get(component_name)
        if component_info is not None:
            return self._get_component_class(component_info)
        custom_components = self.get_custom_components()
        component_info = custom_components.get(component_name)
        if component_info is not None:
            return self._get_component_class(component_info)

        raise ValueError(f"No component found with name: {component_name}")

    @staticmethod
    def _get_custom_components(
        component_file_name: str, strict: bool = False
    ) -> Dict[str, ComponentImport]:
        """Builds a custom component dictionary for importing.

        Args:
            component_file_name (str): The name of the file that contains the custom components.
            strict (bool, optional): Whether to raise an error if a problem is encountered.
                Defaults to False.

        Returns:
            Dict[str, ComponentImport]: The custom component import info. All custom components
                start with custom/ for their name.
        """

        component_json_path = f"{Config.get_imports_components()}/{component_file_name}"
        custom_components: Dict[str, ComponentImport] = {}
        try:
            with open(component_json_path, "r", encoding="UTF-8") as component_file:
                json_components = json.load(component_file)
        except FileNotFoundError:
            EventHandler.get().handle(DebugEvent({"message": "Could not find components file."}))
            json_components = {}
        EventHandler.get().handle(
            DebugEvent({"message": f"Importing custom batchers from: {component_json_path}"})
        )
        if not isinstance(json_components, Dict):
            message = f"Malformed custom component file: {component_json_path}"
            if strict:
                raise ValueError(message)
            EventHandler.get().handle(DebugEvent({"message": message}))
            return custom_components

        for name, import_info in json_components:
            if not isinstance(name, str):
                message = f"Invalid name: {name}"
                if strict:
                    raise ValueError(message)
                EventHandler.get().handle(DebugEvent({"message": message}))
                continue
            try:
                custom_components[f"custom/{name}"] = ComponentImport.from_data(import_info)
            except DaciteError as err:
                if strict:
                    raise err
                EventHandler.get().handle(DebugEvent({"message": str(err)}))
        return custom_components

    def _get_component_class(
        self,
        component_info: ComponentImport,
    ) -> Type[T]:
        """Gets the class from the ComponentImport info.

        Args:
            component_info (ComponentImport): The info required to import the component.

        Returns:
            Type[T]: The class for the component.
        """

        module = importlib.import_module(component_info.module)
        assert hasattr(module, component_info.class_name)
        component = getattr(module, component_info.class_name)
        assert isinstance(component, type), "Component is not a class"
        assert issubclass(
            component, self._type
        ), f"Component must be a subclass of {str(self._type)}"
        return component
