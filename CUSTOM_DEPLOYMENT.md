# **Extending For Your Organization**

### **Custom Components**

AutoTransform is a generic framework for defining automated code transformations, but may not provide all components needed by your specific organization. Fret not, AutoTransform is built to be extended!

If no existing components support the use case needed for your organization, custom components can be used with AutoTransform. Creating a custom component is a fairly straight forward process. First, you need to write a new component class that inherits from the base for the type of component you are building (i.e. [Transformer](https://github.com/nathro/AutoTransform/blob/master/src/python/autotransform/transformer/base.py) for a new Transformer component). Once that component is written and included in your python path, you need to add it to the custom component importing that AutoTransform uses.

Custom components are imported using a JSON encoded files where the files are of the format:
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

An example Pull Request which adds a formatting transformer and associated schema can be found [here](https://github.com/nathro/ATTest/pull/32).

The pieces of this Pull Request are the following:
 - A new component is added in `autotransform/components/atexample/format.py` along with an `__init__.py` file to set up a python package. The transformer here is a simple example that is redundant with existing components, but demonstrates how one might write a format Transformer.
 - The config is updated to point at `autotransform/components` as the location where the custom component JSON files are located.
 - The new component is added to `transformer.json` under the name `format`.
 - This new component is used in the schema `format.json` using the name `custom/format` (all custom components are prefixed with `custom/`).
 - The Python path in the workflow files is updated to point at where the new module is. If you release or use custom components using some packaging service (i.e. PyPI) this step may not be needed and the packages containing the modules can simply be included in requirements files.

New components of all types (i.e. Inputs, Filters, Batchers, etc...) can be added in the same way.

If changes are required beyond simply importing components, feel free to fork the repo! The recommendation, however, is to attempt to use custom imports as much as possible and avoid forking. Feel free to additionally push improvements upstream, think about what changes might make sense to AutoTransform to support your use case or new components that could benefit the community and submit a pull request!

### **Configuration**

When deploying AutoTransform to production, it is highly recommend to handle configuration through the EnvironmentVariableConfigFetcher. Leveraging this, along with setup scripts for developer machines, will allow easy deployment across developer machines as well as CI systems.

### **Remote Runs**

In larger team settings, local runs are likely not the ideal solution. For these cases, it is strongly advised to create a Runner component that integrates with your systems so that work can be run on remote machines. If your codebase uses Github and supports Github Actions, the initialization script `autotransform init` can get you set up quickly. For extremely large codebases, you may additionally need to set up a Runner that uses a queueing system to distribute work across multiple machines. Ensure that the github_token for your workflow has all needed permission (pushing branches, creating/managing pull requests, and triggering actions).

### **Branch Protection Rules**

If your organization uses Github, using a branch protection rule to ensure only the bot is able to push to the branches used for AutoTransform Pull Requests is strongly recommended. This rule should target branches of the form `AUTO_TRANSFORM/**/*` allowing creation, pushes, force pushes, and deletions for the bot alone. Ensuring the security of these changes is important to maintain the security of the repository.