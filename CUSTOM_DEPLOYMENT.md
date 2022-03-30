# Extending For Your Organization

AutoTransform is a generic framework for defining automated code transformations, but may not provide all components needed by your specific organization. Fret not, AutoTransform is built to be extended!

Custom components can be added through config based importing. The custom_components setting in the IMPORTS section of sample_config.ini shows how to import the modules, with an example module shown in `autotransform.thirdparty.example`. If changes are required beyond simply importing new modules, feel free to fork the repo! The recommendation, however, is to attempt to use custom imports as much as possible and avoid forking. Think about what changes might make sense to AutoTransform to support your use case and submit a PR!

#### Remote Runs

For extremely large codebases, running all transformations locally can become unwieldy. For these cases, it is strongly advised to create a remote Worker class that integrates with your systems so that work can be distributed across multiple machines. The simplest way to do this is to implement a Worker that extends RunnableWorker, have the start function set up the call to your remote machines, and on those machines call the spawn_proc function to get the Worker going.