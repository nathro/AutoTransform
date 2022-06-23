# **Managing Changes**

AutoTransform provides a managing command for managing outstanding Changes. Possible actions include things like updating, merging, or abandoning Changes.

### **Manage File**

To manage outstanding Changes, a JSON file with all manager information is required. The manage format looks like the following:
```
{
    "repo": {
        "name": <RepoName>,
        ...
    },
    "runner": {
        "name": <RunnerName>,
        ...
    },
    "steps": [
        {
            "name": <StepName>,
            ...
        },
        ...
    ]

}
```
To see an example, check out `examples/manager.json`.

### **Managing Settings**

* **Repo**: The Repo to fetch outstanding Changes for.
* **Runner**: The Runner to use for updating outstanding Changes.
* **Steps**: The Steps to check against the outstanding Changes.

### **Invoking Management**

Management is invoked using `autotransform manage --path=<path_to_manager_file>`. If the path option is left off, it will default to assuming the manager is located at `autotransform/manager.json`. If you use Github, you can see an example workflow at `examples/workflows/autotransform.manage.yml` that shows how to use Github actions for automating manager runs. If you do not use Github, you can set up a cron job on your organization's infrastructure to invoke the script on a schedule.

As a note, if using GithubActions, the github_token used must have admin access to the repo to trigger further Github actions.

### **Updating your Manager**

`autotransform --manager --update` can be run to update your existing manager information. Leave off the `--update` option to view the existing manager.