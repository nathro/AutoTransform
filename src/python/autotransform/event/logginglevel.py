# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The logging level for an Event. Determines how an event is handled, such
as if it is written to console.
"""


from enum import Enum


class LoggingLevel(int, Enum):
    """The level of an Event, used to determine how it is handled."""

    ERROR = 0
    WARNING = 1
    INFO = 2
    DEBUG = 3
