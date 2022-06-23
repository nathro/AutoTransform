# **Extending For Your Organization**

AutoTransform is a generic framework for defining automated code transformations, but may not provide all components needed by your specific organization. Fret not, AutoTransform is built to be extended!

Custom components can be added through config based importing. Custom components are imported using a JSON encoded files where the files are of the format:
```
{
    "<component_name>": {
        "class_name": "<The name of the class>",
        "module": "<Fully qualified module containing the class>"
    },
    ...
}
```
The `component_directory` setting in the config represents the directory where these files are stored. Each component type has a file in this directory, i.e. `batchers.json`. These can easily be modified through the `autotransform settings --custom-components --update` command. Leaving off `--update` will simply display existing import information.

If changes are required beyond simply importing components, feel free to fork the repo! The recommendation, however, is to attempt to use custom imports as much as possible and avoid forking. Feel free to additionally push improvements upstream, think about what changes might make sense to AutoTransform to support your use case and submit a pull request!

### **Configuration**

When deploying AutoTransform to production, it is highly recommend to handle configuration through the EnvironmentVariableConfigFetcher. Leveraging this, along with setup scripts for developer machines, will allow easy deployment across developer machines as well as CI systems.

### **Remote Runs**

In larger team settings, local runs are likely not the ideal solution. For these cases, it is strongly advised to create a Runner component that integrates with your systems so that work can be run on remote machines. If your codebase uses Github and supports Github Actions, the initialization script `autotransform init` can get you set up quickly. For extremely large codebases, you may additionally need to set up a Runner that uses a queueing system to distribute work across multiple machines. Ensure that the github_token for your workflow has all needed permission (pushing branches, creating/managing pull requests, and triggering actions).