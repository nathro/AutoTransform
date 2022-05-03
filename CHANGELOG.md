# Change Log

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