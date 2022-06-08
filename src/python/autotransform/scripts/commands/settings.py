# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The settings command is used to update AutoTransform settings, such as scheduler.json files,
manager.json files, configs and imported components."""

import json
import os
from argparse import ArgumentParser, Namespace

from autotransform.config.config import Config
from autotransform.config.default import DefaultConfigFetcher
from autotransform.util.component import ComponentFactory, ComponentImport
from autotransform.util.console import choose_option_from_list, error, get_str, info
from autotransform.util.package import get_config_dir


def add_args(parser: ArgumentParser) -> None:
    """Adds the args to a subparser that are required to update/view settings.

    Args:
        parser (ArgumentParser): The parser for the command.
    """

    setting_type_group = parser.add_mutually_exclusive_group(required=True)
    setting_type_group.add_argument(
        "--user-config",
        dest="setting_type",
        action="store_const",
        const="user_config",
        help="Update or view the user configuration for AutoTransform",
    )
    setting_type_group.add_argument(
        "--repo-config",
        dest="setting_type",
        action="store_const",
        const="repo_config",
        help="Update or view the repo configuration for AutoTransform",
    )
    setting_type_group.add_argument(
        "--cwd-config",
        dest="setting_type",
        action="store_const",
        const="cwd_config",
        help="Update or view the current working directory configuration for AutoTransform",
    )
    setting_type_group.add_argument(
        "--custom_components",
        dest="setting_type",
        action="store_const",
        const="custom_components",
        help="Update or view custom components",
    )

    parser.add_argument("--update", dest="update_settings", action="store_true")

    parser.set_defaults(func=settings_command_main, update_settings=False)


def settings_command_main(args: Namespace) -> None:
    """The main method for the settings command, handles the actual execution of updating
    and viewing settings.

    Args:
        args (Namespace): The arguments supplied to the settings command.
    """

    if args.setting_type == "user_config":
        path = f"{get_config_dir}/{DefaultConfigFetcher.FILE_NAME}"
        config = Config.read(path)
        info(f"Current User Config: {config!r}")
        if args.update_settings:
            config.from_console(config, user_config=True)[0].write(path)
    elif args.setting_type == "repo_config":
        path = f"{DefaultConfigFetcher.get_repo_config_dir()}/{DefaultConfigFetcher.FILE_NAME}"
        config = Config.read(path)
        info(f"Current Repo Config: {config!r}")
        if args.update_settings:
            config.from_console(config, user_config=False)[0].write(path)
    elif args.setting_type == "cwd_config":
        path = f"{DefaultConfigFetcher.get_cwd_config_dir()}/{DefaultConfigFetcher.FILE_NAME}"
        config = Config.read(path)
        info(f"Current CWD Config: {config!r}")
        if args.update_settings:
            config.from_console(config, user_config=False)[0].write(path)
    elif args.setting_type == "custom_components":
        component_file_name = choose_option_from_list(
            "Select a component type:",
            [
                ("input.json", "Inputs"),
                ("filter.json", "Filters"),
                ("batcher.json", "Batchers"),
                ("transformer.json", "Transformers"),
                ("validator.json", "Validators"),
                ("repo.json", "Repos"),
                ("schema_builder.json", "Schema Builders"),
                ("runner.json", "Runners"),
                ("item.json", "Items"),
                ("change.json", "Changes"),
                ("step.json", "Steps"),
                ("condition.json", "Conditions"),
            ],
        )
        component_dict = ComponentFactory.get_custom_components_dict(
            component_file_name, strict=False
        )
        if component_dict:
            info("Custom components:")
            for name, component_import in component_dict.items():
                info(f"{name}: {component_import!r}")
        else:
            info("No existing custom components")
        if args.update_settings:
            changed = False

            # Remove components
            if component_dict:
                component_to_remove = get_str("Enter a component name to remove(blank to skip): ")
            else:
                component_to_remove = ""
            while component_to_remove != "":
                if not component_to_remove.startswith("custom/"):
                    component_to_remove = f"custom/{component_to_remove}"
                if component_dict.pop(component_to_remove, None) is None:
                    error(f"No component import with name: {component_to_remove}")
                else:
                    changed = True
                if component_dict:
                    component_to_remove = get_str(
                        "Enter a component name to remove(blank to skip): "
                    )
                else:
                    component_to_remove = ""

            # Add components
            name = get_str("Enter component name to add(blank to skip): ")
            while name != "":
                if not name.startswith("custom/"):
                    name = f"custom/{name}"
                    info("Custom component names must start with custom/, adding prefix")
                if name in component_dict:
                    error("A component with that name already exists.")
                else:
                    class_name = get_str("Enter the class representing this component: ")
                    module = get_str("Enter the fully qualified name of the module for the class: ")
                    component_dict[name] = ComponentImport(class_name=class_name, module=module)
                    changed = True
                name = get_str("Enter component name to add(blank to skip): ")

            if changed:
                file_path = ComponentFactory.get_custom_components_path(component_file_name)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "w+", encoding="UTF-8") as component_file:
                    component_file.write(
                        json.dumps({k: v.bundle() for k, v in component_dict.items()}, indent=4)
                    )
                    component_file.flush()
