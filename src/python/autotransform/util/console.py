# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Utility methods for getting user input for AutoTransform."""

from getpass import getpass
from typing import List, Optional, Tuple, TypeVar

from colorama import Fore

T = TypeVar("T")

ERROR_COLOR = Fore.RED
INFO_COLOR = Fore.YELLOW
INPUT_COLOR = Fore.GREEN
RESET_COLOR = Fore.RESET


def info(text: str) -> None:
    """Prints a string of text as info to the console.

    Args:
        text (str): The text to print.
    """

    print(f"{INFO_COLOR}{text}{RESET_COLOR}")


def error(text: str) -> None:
    """Prints a string of text as error to the console.

    Args:
        text (str): The text to print.
    """

    print(f"{ERROR_COLOR}{text}{RESET_COLOR}")


def get_str(prompt: str, secret: bool = False) -> str:
    """Prompts the user to input a value.

    Args:
        prompt (str): The prompt to give to the user
        secret (bool, optional): Whether to use getpass for input. Defaults to False.

    Returns:
        str: The input value.
    """

    if secret:
        return getpass(f"{INPUT_COLOR}{prompt}{RESET_COLOR}")
    return input(f"{INPUT_COLOR}{prompt}{RESET_COLOR}")


def input_string(
    prompt: str,
    name: str,
    previous: Optional[str] = None,
    default: Optional[str] = None,
    secret: bool = False,
) -> str:
    """Prompts the user to input a value, or potentially use a previously input value/default value.

    Args:
        prompt (str): The prompt to give to the user.
        name (str): The name of the value being prompted for.
        previous (Optional[str], optional): The previously input value. Defaults to None.
        default (Optional[str], optional): The default value. Defaults to None.
        secret (bool, optional): Whether to use getpass for inputs. Defaults to False.

    Returns:
        str: The value entered by the user.
    """

    # Check if the previous value should be used
    # Ignore previous value if it is the same as default
    if (
        previous is not None
        and previous != default
        and choose_yes_or_no(f"Use previous {name} ({previous})?")
    ):
        return previous

    # Check if the user wants to use the default value
    if default is not None and choose_yes_or_no(f"Use default {name}?"):
        return default

    return get_str(f"{prompt} ", secret)


# pylint: disable=too-many-branches
def input_ints(
    prompt: str,
    min_val: Optional[int] = None,
    max_val: Optional[int] = None,
    min_choices: int = 1,
    max_choices: int = 1,
) -> List[int]:
    """Gets integers input from the user within the specified range.

    Args:
        prompt (str): The prompt to give the user.
        min_val (Optional[int], optional): The minimum acceptable value. Defaults to None.
        max_val (Optional[int], optional): The maximum acceptable value. Defaults to None.
        min_choices(int, optional): The minimum number of selections to be made. Defaults to 1.
        max_choices(int, optional): The maximum number of selections to be made. Defaults to 1.

    Returns:
        List[int]: The integers specified by the user.
    """

    assert min_choices >= 0
    assert max_choices >= min_choices
    if min_val is not None and max_val is not None:
        assert min_val <= max_val, "The minimum valid value must be less than the maximum"
        assert max_val - min_val + 1 >= max_choices
        if max_val - min_val + 1 == min_choices:
            return list(range(min_val, max_val + 1))
        range_str = f"({min_val}-{max_val})"
    elif min_val is not None:
        range_str = f"(>={min_val})"
    elif max_val is not None:
        range_str = f"(<={max_val})"
    else:
        range_str = ""

    if max_choices > 1 and min_choices == 0:
        choice_str = "(separate selections with commas, blank to choose none)"
    elif max_choices > 1:
        choice_str = "(separate selections with commas)"
    elif min_choices == 0:
        choice_str = "(blank to choose none)"
    else:
        choice_str = ""

    while True:
        str_val = get_str(f"{prompt}{range_str}{choice_str}: ")
        if max_choices > 1:
            vals = [val.strip() for val in str_val.split(",")]
        else:
            vals = [str_val.strip()]
        int_vals = []
        if min_choices == 0:
            vals = [val for val in vals if val != ""]
        invalid_value = False
        for val in vals:
            if val.startswith("-"):
                is_negative = True
                val = val[1:]
            else:
                is_negative = False
            if not val.isdigit():
                error("Only a decimal number may be entered")
                invalid_value = True
                break
            int_val = -int(val) if is_negative else int(val)
            if min_val is not None and int_val < min_val:
                error(f"{int_val} is too low, must be at least {min_val}")
                invalid_value = True
                break
            if max_val is not None and int_val > max_val:
                error(f"{int_val} is too high, must be less than {max_val}")
                invalid_value = True
                break
            int_vals.append(int_val)
        if invalid_value:
            continue
        if len(vals) > max_choices:
            error(f"Too many selections, only {max_choices} allowed: {vals}")
            continue
        if len(vals) < min_choices:
            error(f"Too few selections, at least {min_choices} required: {vals}")
            continue
        return int_vals


def input_int(
    prompt: str,
    min_val: Optional[int] = None,
    max_val: Optional[int] = None,
) -> int:
    """Gets an integer input from the user within the specified range.

    Args:
        prompt (str): The prompt to give the user.
        min_val (Optional[int], optional): The minimum acceptable value. Defaults to None.
        max_val (Optional[int], optional): The maximum acceptable value. Defaults to None.

    Returns:
        int: The integer specified by the user.
    """

    return input_ints(prompt, min_val=min_val, max_val=max_val)[0]


def choose_option(prompt: str, options: List[Tuple[T, List[str]]]) -> T:
    """Prompts the user to choose one of a set of options using a string. User input is
    converted in to lower case.

    Args:
        prompt (str): The prompt to give the user.
        options (List[Tuple[T, List[str]]]): The potential options to choose. The first value
            is the option, the second value is a list of potential aliases for the option.

    Returns:
        str: The selected option
    """

    assert len(options) > 0, "Choosing from an empty list of options is not possible."
    option_list = [option[1][0] for option in options]
    while True:
        choice = get_str(f"{prompt}({'/'.join(option_list)}) ").lower()
        for option in options:
            if choice in option[1]:
                return option[0]

        error(f"Invalid choice, choose one of: {', '.join(option_list)}")


def choose_yes_or_no(prompt: str) -> bool:
    """Gives the user a yes or no prompt.

    Args:
        prompt (str): The prompt to give to the user.

    Returns:
        bool: If the user chose yes.
    """

    return choose_option(prompt, [(True, ["yes", "y"]), (False, ["no", "n"])])


def choose_options_from_list(
    prompt: str, options: List[Tuple[T, str]], min_choices: int = 1, max_choices: int = 1
) -> List[T]:
    """Prompts the user to choose one of a set of options using a list
    and having the user choose a number.

    Args:
        prompt (str): The prompt for the user.
        options (List[Tuple[T, str]]): The options to choose from, where the first value
            in a Tuple is the option and the second value is the prompt for the list.
        min_choices(int, optional): The minimum number of selections to be made. Defaults to 1.
        max_choices(int, optional): The maximum number of selections to be made. Defaults to 1.

    Returns:
        List[T]: The chosen options.
    """

    assert len(options) > 0, "Choosing from an empty list of options is not possible."
    for idx, option in enumerate(options):
        print(f"{INPUT_COLOR}{idx + 1}) {option[1]}{RESET_COLOR}")
    choices = input_ints(
        prompt,
        min_val=1,
        max_val=len(options),
        min_choices=min_choices,
        max_choices=max_choices,
    )
    return [options[choice - 1][0] for choice in choices]
