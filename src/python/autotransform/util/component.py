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
from typing import Any, ClassVar, Dict, Generic, Optional, Type, TypeVar

from dacite import from_dict

from autotransform.config import fetcher as Config
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler


@dataclass(frozen=True)
class ComponentImport:
    """The information required to import and return a component."""

    class_name: str
    module: str


TComponent = TypeVar("TComponent")


class Component(ABC):
    """A base class for AutoTransform components, such as Batchers."""

    name: ClassVar[str]

    def bundle(self) -> Dict[str, Any]:
        """Generates a JSON encodable bundle.
        If a component is not JSON encodable this method should be overridden to provide
        an encodable version.

        Returns:
            Dict[str, Any]: The encodable bundle.
        """
        return {"name": self.name} | asdict(self)

    @classmethod
    def from_data(cls: Type[TComponent], data: Dict[str, Any]) -> TComponent:
        """Produces an instance of the component from decoded data. Override if
        the component had to be modified to encode.

        Args:
            data (Mapping[str, Any]): The JSON decoded data.

        Returns:
            TComponent: An instance of the component.
        """

        return from_dict(data_class=cls, data=data)


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
    _custom_components: Dict[str, ComponentImport]
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

        if not hasattr(self, "_custom_components"):
            self._custom_components = ComponentFactory._get_custom_components(
                self._custom_components_file, strict
            )
        return self._custom_components

    def get_instance(self, data: Dict[str, Any]) -> T:
        """Simple method to get an instance from a bundle.

        Args:
            data (Dict[str, Any]): The bundled component.

        Returns:
            T: An instance of the associated component.
        """

        return self.get_class(data["name"]).from_data(data)

    def get_class(self, component_type: str) -> Type[T]:
        """Gets the class for a component with the specified type, usually an enum value.

        Args:
            component_type (str): The type of the component, usually an enum value. If a custom
                component is used, the type should start with custom/.

        Raises:
            ValueError: If the component could not be found.

        Returns:
            Type[T]: The class for the component.
        """

        component_info = self.get_components().get(component_type)
        if component_info is not None:
            return self._get_component_class(component_info)
        custom_components = self.get_custom_components()
        component_info = custom_components.get(component_type)
        if component_info is not None:
            return self._get_component_class(component_info)

        raise ValueError(f"No component found with type: {component_type}")

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
            if not isinstance(import_info, Dict):
                message = f"Invalid import: {json.dumps(import_info)}"
                if strict:
                    raise ValueError(message)
                EventHandler.get().handle(DebugEvent({"message": message}))
                continue
            component_import = ComponentFactory._get_component_import(import_info, name, strict)
            if component_import is not None:
                custom_components[f"custom/{name}"] = component_import
        return custom_components

    @staticmethod
    def _get_component_import(
        import_info: Dict, name: str, strict: bool = False
    ) -> Optional[ComponentImport]:
        """Gets the component import info from a JSON decoded dictionary.

        Args:
            import_info (Dict): The JSON decoded import information.
            name (str): The name of the component.
            strict (bool, optional): Whether to raise an error if a problem is encountered.
                Defaults to False.

        Raises:
            ValueError: Raised if using strict imports and an issue is encountered during
                the creation of the ComponentImport.

        Returns:
            Optional[ComponentImport]: The ComponentImport needed to get the component class.
                None if there is an issue with the info.
        """

        class_name = import_info.get("class_name")
        if class_name is None:
            message = f"Class name missing for {name}"
            if strict:
                raise ValueError(message)
            EventHandler.get().handle(DebugEvent({"message": message}))
            return None
        if not isinstance(class_name, str):
            message = f"Invalid class name for {name}: {class_name}"
            if strict:
                raise ValueError(message)
            EventHandler.get().handle(DebugEvent({"message": message}))
            return None
        module = import_info.get("module")
        if module is None:
            message = f"Module missing for {name}"
            if strict:
                raise ValueError(message)
            EventHandler.get().handle(DebugEvent({"message": message}))
            return None
        if not isinstance(module, str):
            message = f"Invalid module for {name}: {module}"
            if strict:
                raise ValueError(message)
            EventHandler.get().handle(DebugEvent({"message": message}))
            return None
        return ComponentImport(class_name, module)

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
