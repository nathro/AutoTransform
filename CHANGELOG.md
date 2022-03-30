# Change Log

## Upcoming Release

#### New Components

 - EnvironmentVariableConfigFetcher: A config fetcher that pulls values from environment variables

#### Scripts

 - Run and instance scripts have been migrated to the main script
 - Config command added to main scripts for listing or updating config.ini values

#### API Changes

 - Transformer: Transform now takes Batch instead of Cached File

#### Upgrade Packages

#### Misc

- Manager script renamed to run, now invoked as atrun
- RunnableWorker renamed to ProcessWorker
- Runner renamed to Coordinator
- Updated BatchMetadata to only require title
- Add a generic to components for params so that type safety is improved
- Changed how custom components are expected to be handled, now being imported through a config setting

## Release 0.1.1 - Initial Beta!

This is the first official release of AutoTransform! Please check out the readme for functionality and explore our scripts/components. If you're interested in contributing check out CONTRIBUTING.md. If you're looking to deploy an instance with bespoke components for your organization, check out CUSTOM_DEPLOYMENT.md.