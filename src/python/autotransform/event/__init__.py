# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Events are used by AutoTransform for the purposes of logging. The EventHandler can be used
as an entry point for hooks in to the Event framework for logging to an organization's specific
datastore. Custom hooks can be added through the environment variable AUTO_TRANSFORM_EVENT_HANDLER.
Set that environment variable to a JSON map of:
{"class_name": <Class that inherits from EventHandler>, "module": <Module the class is in>}
to insert your own hook in to AutoTransform event handling.
"""
