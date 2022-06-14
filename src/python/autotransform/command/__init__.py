# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Commands take a Batch that has already been transformed and perform post-processing
steps before the Batch is submitted, such as code generation. These steps can be performed
either pre or post-validation, depending on if the run_pre_validation flag is set."""
