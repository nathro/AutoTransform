# Change Log

## Release 1.1.0

### Migrations
 - The schema map has been upgraded to use SchemaMap class, with all file targets now relative to the directory that contains the schema map.
 - Significant updates have been made to how Script components work. They now use keys as a list replacement (i.e. ["foo", "<<KEY>>"] becomes ["foo", "bar.py", "baz,py"]). Additionally, extra data always maps key to the extra data, even for single transformations.
 - ScriptTransformer no longer has a per_item parameter, using chunk_size to allow chunking of items instead. per_item will be treated as chunk_size = 1. This legacy support will be disabled in 1.3.0.
 - DirectoryInput now accepts a paths parameter with a list of paths to use instead of a singular string from path. The path parameter will continue to be supported until 1.3.0. DirectoryInput also now strips ./ from the front of file paths to maintain consistency in path structure when using the "." directory.

### Features
 - Added an optional repo_override setting to Config that can be used to override the repo of supplied schemas
 - Added AUTO_TRANSFORM_SCHEMA_MAP_PATH environment variable support to override default schema_map path
 - Script components now can take a replacement dictionary as the environment variable AUTO_TRANSFORM_SCRIPT_REPLACEMENTS
 - Added target_repo_name and target_repo_ref to GithubRunner so that workflow can control checkout with inputs, makes having a single repo that acts on all of your repos a bit better
 - Added maximum batch size option to CodeownersBatcher
 - Updates GithubRepo to use gists for storing batch/schema information. GithubChange can still use the old system but that support will be deprecated with 1.3.0

### New Components
 - AggregateFilter a filter that aggregates other filters
 - CodeownersFiler a filter that passes only files with the specified owner

### Misc
 - Redact github_token and jenkins_token fields from Config
 - Significantly updated logging to separate pure debugging information from simple verbose logs

### Bugs
 - Fixes reviewers being requested for CodeownersBatcher when the metadata doesn't have the field present

## Release 1.0.7

### New Components
 - MergeableStateCondition

### Fixes
 - Fixed an issue with user config not saving to the right location when using settings command
 - Fixed an issue where get_open_pull_requests didn't work for GithubRepos with large numbers of open PRs

### Misc
 - Manage command can now be run using a local runner
 - Schedule command can now be run using a local runner

## Release 1.0.6

### New Components
 - RequestStrCondition
 - CodeownersBatcher

### Features
 - Support GithubRunner using repos outside the schema's repo to trigger workflows.
 - Make GitRepo strip some bad substrings from branch names

### Fixes
 - Made the GitGrepInput no longer include repo dir in the name of the file. This is unneeded for accessing the file and causes bad behavior when combined with things that use file names that are run on remote machines

## Post Release 1.0.5
 - Fixed migration scripts

## Release 1.0.5

### Migrations
 - Split out review/test/change states to be separate.
 - atmigrate-1.0.5 to migrate Manager for 1.0.5 changes. Can not handle in/not_in comparisons for ChangeStateCondition

#### New Components
 - JenkinsAPIRunner
 - JenkinsFileRunner
 - RequestAction
 - ReviewStateCondition
 - TestStateCondition

#### New Features
 - Added bash scripts and dockerfile to allow for deploying using Docker

#### Misc
 - Remove take_action from Change and put logic in Action method run()
 - Removed Runner from Scheduler/Manager and allowed them to just use runner from config

## Release 1.0.4

#### New Features
 - Added Schema Map to settings so to ease updating/viewing the schema map.

#### Fixes
 - Fix Scheduler from_console command to account for new Scheduler format, fixing `autotransform settings` to work for updating schedule.
 - Fix Scheduler usage of sample schema.

## Release 1.0.3

#### Migrations
 - GithubRunner has been updated to work with the new workflows included in examples. This requires use of the schema_map.json file and having the workflows use the schema names, rather than JSON encoded schemas. This ensures that any schema run by the bot is present in the repo. Replace existing workflows with new workflows in `examples/workflows`.
 - Updated migration commands.
  - atmigrate-1.0.1 to migrate Manager for 1.0.1 changes.
  - atmigrate-1.0.3 to migrate Scheduler/Schema Map for 1.0.3 changes.

#### Documentation
 - Added documentation for creating and using custom components, including an example PR.

#### New Components
 - Added ExtraDataBatcher that allows batching items using the extra_data field of the items.
 - Added FileRegexBatcher that allows using regexes against file contents to produces batches with metadata.

#### Features
 - Added a max_submissions option to schema configs and scheduling to allow slower rollouts for changes that can prevent overwhelming code review.
 - Update Change to have get_schema_name() that is used for Condition. This allows GithubChange to pull schema name from the branch.
 - Add a schema_map.json file and some associated functionality to run command so that workflows can be moved to rely on information in the repo when determining schemas and no longer pass JSON encoded schemas around.
 - Make run github workflow use the schema name.
 - Added in/not in comparisons.

#### Fixes
 - Fix workflows to checkout the repo as the supplied bot, rather than as github-actions bot. This should prevent issues involving branch protection rules and force-pushes appearing under the wrong name.

## Release 1.0.2

#### New Components
 - InlineInput for inlining Items.
 - InlineFileInput for inline FileItems.
 - InlineGenericInput for inlining Items using keys.
 - LibCSTTransformer for libcst based transformations. Check out https://github.com/Instagram/LibCST for info on libcst.
 - JSCodeshiftTransformer for jscodeshift based transformations. Check out https://github.com/facebook/jscodeshift for info on JSCodeshift.

#### Features
 - Update GithubRepo to use a dataclass for metadata to improve type safety/checking.
 - Update GithubRepo to allow Pull Requests from forks.
 - Updated debug logging to be more readable and include appropriate information.

## Release 1.0.1

This update focuses on improvements to managing changes, increasing the power of actions and adding many more actions.

#### Migrations
 - autotransform.scripts.migrations.manager migration script for migrating Manager JSON files.
 - Run `atmigrate-manager` to migrate Manager JSON files.
 - Step components now return a List of Actions, which are now fully-fledged NamedComponents. This is simply moving from an enum to a class for most cases.
 - Step components now have a method to check if management should be continued.
 - Changed comparison enum values, migrate with the migration script for Manager files.
 - Conditional steps now take a list of actions instead of an action name. Old JSON will maintain compatability until v1.1.

 #### Features
 - Updated repos to check for outstanding changes before running a Batch. If an outstanding change is found (the branch already exists for Git/Github), transformation is skipped.
 - Made Actions fully-fledged components to enable Actions with parameters.

#### New Components
 - AddReviewersAction added.
 - AddOwnersAsReviewersAction added.
 - AddOwnersAsTeamReviewersAction added.
 - AddLabelsAction added.
 - CommentAction added.
 - RemoveLabelAction added.
 - ReviewersCondition added.
 - TeamReviewersCondition added.
 - LabelsCondition added.

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