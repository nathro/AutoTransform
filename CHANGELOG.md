# Change Log

## Release 1.0.1

#### Migrations
 - Custom Step components now return a List of Actions, which are now fully-fledged NamedComponents. This is simply moving from an enum to a class for most cases.
 - Custom Step components now have a method to check if management should be continued.

#### Components
 - Updated repos to check for outstanding changes before running a Batch. If an outstanding change is found (the branch already exists for Git/Github), transformation is skipped.
 - Made Actions fully-fledged components to enable Actions with parameters.
 - AddReviewersAction added.

## Release 1.0.0

AutoTransform is officially available for production use cases. See our documentation at autotransform.readthedocs.io to learn more about how it works and how it can save your organization thousands of developer hours.

#### Components
 - Renamed base_branch_name to base_branch for GitRepo

## Release 0.3.1

#### Components
 - Added reviewer functionality to GithubRepo
 - Renamed required_labels to labels for GithubRepo

#### Misc
 - Moved off of python dataclasses to Pydantic
 - Modified scheduler file format to have "target" instead of "schema" for the path/builder name of the scheduled schemas
 - Converted AutoTransformSchema and SchemaConfig to use ComponentModel base

#### Scripts
 - Moved config setting/viewing to settings command which will include all settings
 - Added custom components to settings command
 - Added manager to settings command
 - Added scheduler to settings command
 - Added schema to settings command
 - Made files options for schedule/manage commands, no longer positional arguments

## Release 0.3.0 - Production Beta

#### API Changes
 - Updating all components to inherit from Component class to unify logic for many pieces in one place
 - Eliminated params from components, components are now dataclasses
 - Component bundles use "name" instead of "type" now to avoid confusion between the class type and the identifier
 - Custom components are now imported via JSON files
 - Schedule/manage/config files all converted to JSON based on new dataclasses

#### New Components
 - Added EmptyInput for schemas that operate on the entire codebase at once

#### Scripts
 - Added init command to set up user configuration/repos
 - Replaced config command with one that allows the user to navigate through prompts

#### Misc
 - Updated default config fetcher to pull repo and cwd relative configs
 - Made EnvironmentVariableConfigFetcher use DefaultConfigFetcher as a fallback when no environment variable is present
 - Updated directory structure to src/python/autotransform
 - Broke docs apart for better browsing rather than 1 large readme
 - Added utility functions for the init script involving user input/console output

## Release 0.2.1 - Production Beta

#### API Change
 - Made it so Transformer objects could return a result that would be used by the Repo/Validator/Commands

#### Misc
 - Added an optional owners list to Schemas
 - Added a skip_empty_batch option for SingleBatcher
 - Set minimum versions for requirements in package
 - Replaced PyGithub with ghapi
 - Added configparser requirement

## Release 0.2.0 - Production Beta

Version 0.2.0 represents a production ready beta of AutoTransform. It includes all initial functionality for production environments and represents the desired API for AutoTransform. This API will not be final until 1.0.0 is released, at which point breaking changes will generally only occur with major version updates.

#### New Components

 - EnvironmentVariableConfigFetcher: A config fetcher that pulls values from environment variables
 - GitGrepInput for using git grep to find files
 - DirectoryBatcher for batching files within a directory together
 - ChunkBatcher for chunking Items from Inputs
 - ScriptTransformer as simple transformer that invokes a script
 - RegexFilter as a Filter which checks the Item's key against a regex pattern
 - FileContentRegexFilter as a Filter that checks a file's contents against a regex pattern
 - Added ShardFilter concept and KeyHashShardFilter
 - ScriptValidator for handling validation using command line scripts like mypy or pytest
 - ScriptCommand for running scripts like black for post-processing

 - Runner class added to provide an API for invoking runs
 - GithubRunner class added to use Github workflows for remote runs

 - Change class added to provide an API for handling submissions to source control/code review
 - Step class for managing changes
 - ConditionalStep for condition based actions
 - Condition class for handling step logic
 - UpdateAgoCondition, CreatedAgoCondition, ChangeStateCondition, SchemaNameCondition, AggregateCondition for potential conditions of ConditionalStep

#### Scripts

 - Run script has been migrated to the main script
 - Instance script and regexmod script eliminated
 - Config command added to main scripts for listing or updating config.ini values
 - Updated run script to allow remote runs
 - Added schedule script

#### API Changes

 - Transformer: Transform now takes Batch instead of Cached File
 - Eliminated Worker concept and merged logic in to Runners, which can handle local and remote running
 - Replaced file path strings returned by Inputs with an Item concept that encapsulates extra data, removing the need for DataStore
 - Added current to autotransform.schema to provide globally accessible instance of currently running schema

#### Upgrade Packages

#### Misc

- Updated BatchMetadata to not include title, while title becomes an element of batch
- Add a generic to components for params so that type safety is improved
- Changed how custom components are expected to be handled, now being imported through a config setting
- GithubRepo now uses body param from metadata for PR body
- Added labels option for GithubRepo to attach labels to a PR
- Added Event class and EventHandler class for dispatching events for logs and other hooks
- Added Data/workflows/autotransform_runner.yml as a sample for github workflows

## Release 0.1.1 - Initial Beta!

This is the first official release of AutoTransform! Please check out the readme for functionality and explore our scripts/components. If you're interested in contributing check out CONTRIBUTING.md. If you're looking to deploy an instance with bespoke components for your organization, check out CUSTOM_DEPLOYMENT.md.