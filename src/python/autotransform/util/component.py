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
from enum import Enum
from functools import cached_property
from typing import Any, ClassVar, Dict, Generic, List, Optional, Tuple, Type, TypeVar

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.event.warning import WarningEvent
from autotransform.util.console import (
    choose_options_from_list,
    choose_yes_or_no,
    error,
    get_str,
    info,
)

TComponent = TypeVar("TComponent", bound=BaseModel)

UNSET_VALUE = object()


class ComponentModel(BaseModel):
    """A base class for AutoTransform components that need to handle bundling/unbundling
    for JSON."""

    def bundle(self) -> Dict[str, Any]:
        """Generates a JSON encodable bundle.
        If a component is not JSON encodable this method should be overridden to provide
        an encodable version.

        Returns:
            Dict[str, Any]: The encodable bundle.
        """

        bundle = dict(self._iter(to_dict=False, exclude_defaults=True, exclude_unset=True))
        for key, value in bundle.items():
            if isinstance(value, ComponentModel):
                bundle[key] = value.bundle()
            elif isinstance(value, List) and all(
                isinstance(item, ComponentModel) for item in value
            ):
                bundle[key] = [item.bundle() for item in value]
            elif isinstance(value, Dict) and all(
                isinstance(item, ComponentModel) for item in value.values()
            ):
                bundle[key] = {item_key: item.bundle() for item_key, item in value.items()}

        return bundle

    @classmethod
    def from_data(cls: Type[TComponent], data: Dict[str, Any]) -> TComponent:
        """Produces an instance of the component from decoded data. Override if
        the component had to be modified to encode.

        Args:
            data (Mapping[str, Any]): The JSON decoded data.

        Returns:
            TComponent: An instance of the component.
        """

        return cls.parse_obj(data)

    def __repr__(self) -> str:
        if len(self.__fields__) < 2:
            return super().__repr__()
        lines = [f"{self.__class__.__name__}("]
        for name in self.__fields__.keys():
            field_val = getattr(self, name)
            if isinstance(field_val, list) and len(field_val) > 1:
                lines.append(f"\t{name}=[")
                lines.extend([f"\t\t{val!r},".replace("\n", "\n\t\t") for val in field_val])
                lines.append("\t],")
            elif isinstance(field_val, dict) and len(field_val) > 1:
                lines.append(f"\t{name}=" + "{")
                field_lines = [f"\t\t{key}={val!r}," for key, val in field_val.items()]
                lines.extend([line.replace("\n", "\n\t\t") for line in field_lines])
                lines.append("\t},")
            elif isinstance(field_val, Enum):
                lines.append(f"\t{name}={field_val.value!r},")
            else:
                lines.append(f"\t{name}={field_val!r},".replace("\n", "\n\t"))
        lines.append(")")
        return "\n".join(lines)


class NamedComponent(ComponentModel):
    """A base class for AutoTransform components that are produced from a factory using
    a name to differentiate component classes.

    Attributes:
        name (ClassVar[Enum]): The name of the Component.
    """

    name: ClassVar[Enum]

    def bundle(self) -> Dict[str, Any]:
        """Generates a JSON encodable bundle.
        If a component is not JSON encodable this method should be overridden to provide
        an encodable version.

        Returns:
            Dict[str, Any]: The encodable bundle.
        """

        return {"name": self.name} | super().bundle()


class ComponentImport(ComponentModel):
    """The information required to import and return a component.

    Attributes:
        class_name (str): The name of the class of the component.
        module (str): The fully qualified module where the class can be imported.
    """

    class_name: str
    module: str


T = TypeVar("T", bound=NamedComponent)


class ComponentFactory(Generic[T], ABC):
    """A factory class that produces instances of components

    Attributes:
        _components (Dict[str, ComponentImport]): A mapping from a component name
            to the information needed to import and use that component.
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

        return ComponentFactory.get_custom_components_dict(
            self._custom_components_file, strict=False
        )

    @cached_property
    def _custom_components_strict(self) -> Dict[str, ComponentImport]:
        """A cached property for the strict custom components.

        Returns:
            Dict[str, ComponentImport]: Strict custom components.
        """

        return ComponentFactory.get_custom_components_dict(
            self._custom_components_file, strict=True
        )

    # pylint: disable=too-many-arguments,too-many-branches
    def from_console(
        self,
        name: str,
        previous_value: Optional[T] = UNSET_VALUE,  # type: ignore
        default_value: Optional[T] = UNSET_VALUE,  # type: ignore
        simple: bool = False,
        allow_none: bool = True,
    ) -> Optional[T]:
        """Gets a component from console inputs.

        Args:
            name (str): The name of the component being entered.
            previous_value (Optional[T], optional): A previously used value for the
                component. Defaults to UNSET_VALUE.
            default_value (Optional[T], optional): A default value for the component.
                Defaults to UNSET_VALUE.
            simple (bool, optional): Whether to choose simple options. Defaults to False.
            allow_none (bool, optional): Whether None is a valid value. Defaults to True.

        Returns:
            Optional[T]: The component or None.
        """

        if (isinstance(previous_value, self._type) or (previous_value is None and allow_none)) and (
            simple or choose_yes_or_no(f"Use previous {name}: {previous_value!r}?")
        ):
            return previous_value

        # pylint: disable=too-many-boolean-expressions
        if (
            (isinstance(default_value, self._type) or (default_value is None and allow_none))
            and default_value != previous_value
            and (simple or choose_yes_or_no(f"Use default {name}: {default_value!r}?"))
        ):
            return default_value
        all_components = self.get_components() | self.get_custom_components()
        options: List[Tuple[str, str]] = [(key, key) for key in all_components.keys()]
        component_name = choose_options_from_list(
            f"Choose a {name}", options, min_choices=0 if allow_none else 1
        )
        if allow_none and not bool(component_name):
            return None
        component_class = self.get_class(component_name[0])
        if not bool(component_class.__fields__):
            return component_class.from_data({})
        info(f"{component_class.__name__} Fields:")
        for field_name, field in component_class.__fields__.items():
            # pylint: disable=protected-access
            if field.required:
                info(f"\t{field_name}: {field._type_display()}")
            else:
                info(f"\t{field_name}: {field._type_display()} = {field.get_default()}")

        while True:
            component_json = get_str(f"Enter JSON encoded {component_class.__name__}: ")
            try:
                if component_json != "":
                    component_data = json.loads(component_json)
                else:
                    component_data = {}
                if not isinstance(component_data, Dict):
                    error("Invalid JSON data, must be Dict")
                    continue
                return component_class.from_data(component_data)
            except json.JSONDecodeError as err:
                error(f"Failed to parse JSON\n{err}")
            except TypeError as err:
                error(f"Invalid type found\n{err}")
            except ValueError as err:
                error(f"Invalid value found\n{err}")

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

        names = json.dumps(list(self.get_components().keys() | self.get_custom_components().keys()))
        raise ValueError(f"No component found with name {component_name}, valid names: {names}")

    @staticmethod
    def get_custom_components_dict(
        component_file_name: str, strict: bool = False
    ) -> Dict[str, ComponentImport]:
        """Builds a custom component dictionary for importing.

        Args:
            component_file_name (str): The name of the file that contains the custom components.
            strict (bool, optional): Whether to raise an error if JSON is malformed.
                Defaults to False.

        Returns:
            Dict[str, ComponentImport]: The custom component import info. All custom components
                start with custom/ for their name.
        """

        custom_components: Dict[str, ComponentImport] = {}
        component_json_path = ComponentFactory.get_custom_components_path(component_file_name)
        EventHandler.get().handle(
            DebugEvent({"message": f"Importing custom components from: {component_json_path}"})
        )
        try:
            with open(component_json_path, "r", encoding="UTF-8") as component_file:
                json_components = json.load(component_file)
        except FileNotFoundError:
            EventHandler.get().handle(WarningEvent({"message": "Could not find components file."}))
            json_components = {}
        if not isinstance(json_components, Dict):
            message = f"Malformed custom component file: {component_json_path}"
            if strict:
                raise ValueError(message)
            EventHandler.get().handle(WarningEvent({"message": message}))
            return custom_components

        for name, import_info in json_components.items():
            if not isinstance(name, str):
                message = f"Invalid name: {name}"
                if strict:
                    raise ValueError(message)
                EventHandler.get().handle(WarningEvent({"message": message}))
                continue
            try:
                custom_components[f"custom/{name}"] = ComponentImport.from_data(import_info)
            except Exception as err:  # pylint: disable=broad-except
                if strict:
                    raise err
                EventHandler.get().handle(WarningEvent({"message": str(err)}))
        return custom_components

    @staticmethod
    def get_custom_components_path(component_file_name: str) -> str:
        """Gets the path for the custom component file.

        Args:
            component_file_name (str): The name of the file that contains the custom components.

        Returns:
            str: The path where the custom component JSON is located.
        """
        # Importing here to avoid a cyclic import
        import autotransform.config  # pylint: disable=import-outside-toplevel

        return f"{autotransform.config.CONFIG.component_directory}/{component_file_name}"

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
