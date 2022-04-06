# Change Log

## Upcoming Release

#### New Components

 - EnvironmentVariableConfigFetcher: A config fetcher that pulls values from environment variables
 - GitGrepInput for using git grep to find files
 - DirectoryBatcher for batching files within a directory together
 - ChunkBatcher for chunking inputs
 - ScriptTransformer as simple transformer that invokes a script
 - RegexFilter as a filter which checks the input against a regex pattern

#### Scripts

 - Run and instance scripts have been migrated to the main script
 - Config command added to main scripts for listing or updating config.ini values

#### API Changes

 - Transformer: Transform now takes Batch instead of Cached File

#### Upgrade Packages

#### Misc

- RunnableWorker renamed to ProcessWorker
- Runner renamed to Coordinator
- Updated BatchMetadata to only require title
- Add a generic to components for params so that type safety is improved
- Changed how custom components are expected to be handled, now being imported through a config setting
- GithubRepo now uses body param from metadata for PR body

## Release 0.1.1 - Initial Beta!

This is the first official release of AutoTransform! Please check out the readme for functionality and explore our scripts/components. If you're interested in contributing check out CONTRIBUTING.md. If you're looking to deploy an instance with bespoke components for your organization, check out CUSTOM_DEPLOYMENT.md.