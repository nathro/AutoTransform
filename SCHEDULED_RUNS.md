# **Scheduled Runs**

AutoTransform provides a scheduling component for setting up automatically scheduled runs to maintain a codebase in to the future. Once set up, scheduled runs will ensure that an organization's codebase stays up-to-date.

### **Schedule File**

To get scheduled runs going, a JSON file with all scheduling information is required. The schedule format looks like the following:
```
{
    "base_time": <int>,
    "runner": {
        "name": <RunnerName>,
        ...
    },
    "excluded_days": [<0-6>],
    "schemas": [
        {
            "type": <builder, file>,
            "target": <string>,
            "schedule": {
                "repeats": <daily, weekly>,
                "hour_of_day": <0-23>,
                "day_of_week": <0-6>,
                "shard_filter": {
                    "name": <FilterName>,
                    "num_shards": <int>,
                    ...
                }
            }
        }
    ]
}
```
To see an example, check out `examples/scheduler.json`.

### **Scheduling Settings**

The following settings are used when scheduling schemas to run automatically.
  * **Overall Settings**
    * **base_time**: This serves as the basis for determining hour of day and day of week. When scheduling is invoked, this time is subtracted from the current time to determine day of week and hour of day, with the base time treated as hour 0 on day 0.
    * **runner**: This is an encoded runner object. All schemas that have been scheduled will be run using this object. It should trigger runs on the organization's CI infrastructure.
    * **excluded_days**: A list of days of the week that schemas will not run. Defaults to empty.
    * **schemas**: A list of schemas to schedule.
  * **Schema Settings**
    * **type**: Either the string "builder" or the string "file". This is used to determine whether the value of the schema setting refers to a SchemaBuilderType or a file path.
    * **target**: Either a SchemaBuilderType or a file path.
    * **Schedule**
      * **repeats**: Either the string "daily" or the string "weekly". How often the schema will be run.
      * **hour_of_day**: Which hour of the day, using the logic described for base_time, that the schema will be run. Defaults to 0.
      * **day_of_week**: Which day of the week, using the logic described for base_time, that the schema will be run. Defaults to 0. Only applies to weekly runs.
      * **shard_filter**: A ShardFilter object that will be used to perform the actual sharding. It will get the valid_shard from the scheduler before running.

### **Invoking Scheduled Runs**

Scheduled runs are invoked using `autotransform schedule --path=<path_to_schedule_file>`. If the path option is left off, it will default to assuming the schedule is located at `autotransform/scheduler.json`. If you use Github, you can see an example workflow at `examples/workflows/autotransform.schedule.yml` that shows how to use Github actions for automating scheduled runs. If you do not use Github, you can set up a cron job on your organization's infrastructure to invoke the script on a schedule. Additionally, the `--time=<int>` option can be used to override the current timestamp when calculating hour/day. Using this may be useful if there is potential delay in your automation infrastructure.

As a note, if using GithubActions, the github_token used must have admin access to the repo to trigger further Github actions.

### **Updating your Scheduler**

`autotransform --sheduler --update` can be run to update your existing scheduler information. Leave off the `--update` option to view the existing scheduler.