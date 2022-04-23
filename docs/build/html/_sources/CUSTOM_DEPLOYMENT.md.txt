# **Extending For Your Organization**

AutoTransform is a generic framework for defining automated code transformations, but may not provide all components needed by your specific organization. Fret not, AutoTransform is built to be extended!

Custom components can be added through config based importing. The custom_components setting in the IMPORTS section of sample_config.ini shows how to import the modules, with an example module shown in `autotransform.thirdparty.components`. If changes are required beyond simply importing new modules, feel free to fork the repo! The recommendation, however, is to attempt to use custom imports as much as possible and avoid forking. Feel free to additionally push improvements upstream, think about what changes might make sense to AutoTransform to support your use case and submit a pull request!

## **Configuration**

When deploying AutoTransform to production, it is highly recommend to handle configuration through the EnvironmentVariableConfigFetcher. Leveraging this, along with setup scripts for developer machines, will allow easy deployment across developer machines as well as CI systems.

## **Remote Runs**

In larger team settings, local runs are likely not the ideal solution. For these cases, it is strongly advised to create a Runner component that integrates with your systems so that work can be be run on remote machines. If your codebase uses Github, the GithubRunner component can be used with the example workflow in data/workflows/autotransform_runner.yml. This will allow you to leverage Github Actions for your remote run needs. For extremely large codebases, you may additionally need to set up a Runner that uses a queueing system to distrubute work across multiple machines.