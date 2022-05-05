# **Overview**

Full documentation available [here](https://autotransform.readthedocs.io)

## **Installing**

> **⚠ WARNING:** AutoTransform requires Python 3.10

 - **Latest Release** `pip install AutoTransform`
 - **Bleeding Edge** `pip install git+git://github.com/nathro/AutoTransform.git`
   - Windows users may need to replace `git://` with `https://`
   - If you do not have git use: `pip install https://github.com/nathro/AutoTransform/archive/master.zip`
## **Summary**

AutoTransform is an opensource framework for large-scale code modification. It enables a schema-based system of defining codemods that can then be run using AutoTransform, with options for automatic scheduling as well as change management. AutoTransform leverages a component-based model that allows adopters to quickly and easily get whatever behavior they need through the creation of new, custom components. Additionally, custom components can readily be added to the component library of AutoTransform to be shared more widely with others using the framework.

## **Goal**

The goal of AutoTransform is to make codebase maintenance simple, easy, and automatic. By providing a clear structure for definition, all types of modifications can be automated. Some examples include:

* Library upgrades
* API changes
* Performance improvements
* Lint or style fixes
* Dead code
* One-off refactors
* Any other programmatically definable modification

## **Philosophies**
### **Component Based**

AutoTransform heavily uses a component based model for functionality. This allows easy customization through the creation of new plug-and-play components. Core logic is about funneling information between components, while the components themselves contain business logic. While AutoTransform provides an ever-growing library of components for ease of adoption, bespoke components will always be needed for some use cases.

### **Language Agnostic**

AutoTransform, though written in Python, is a language agnostic framework. Our component model allows AutoTransform to treat each component as a black-box that can leverage whatever tooling or language makes sense for the goal of the component. This is most heavily needed for the components which actually make code changes where leveraging tools for Abstract(or Concrete) Syntax Trees(AST/CST) is often done in the language being modified.

### **Minimal Developer Involvement**

Managing large scale changes can be extremely time consuming, AutoTransform puts automation first with the goal of automating as much of the process as possible. Developer time is incredibly valuable and should be saved for things that actually require it. If a computer can do it, a computer should do it.

## **Example - Typing**

As an example of how AutoTransform might be used, let’s go through the case of typing a legacy codebase. This is a notoriously difficult and time consuming process.

### **Static Inference**

A codemod can be written that statically infers types from the types around whatever needs types. Hooking this up to scheduled runs would mean that as people type your code, other types can later be inferred. Additionally, as the codemod types code, that can reveal further types that can be statically inferred. This would allow typing to slowly build up over time automatically as the codemod runs and developers introduce more types themselves, significantly speeding up the process of typing a legacy codebase.

### **Run Time Logging**

In addition to static typing, a codemod could instrument untyped functions or other code to log types at run time. These logs could then be fed into the codemod to add types to code that can’t be inferred but can be determined at run time. This codemod could additionally be written to only instrument a small part of the codebase at a given time, preventing excessive resource utilization.

### **The Whole Versus the Sum of the Parts**

Each codemod that can change code can benefit from all other codemods. As run time logging adds types, static inference can make better changes. Dead code removal can clean up untyped code. The layered passes, and building on top of the changes of each codemod, can produce significantly greater wins.

# **Core Functionality**

## **Data Flow**

**[A visual representation](https://lucid.app/lucidchart/eca43a3d-175f-416f-bb4f-4363d56f951b/edit?invitationId=inv_f44ed708-8c4a-4998-96f2-8b860aba8ebc)**

The Input component of the schema will get a list of Items that may serve as inputs to a transformation, these are then passed through the Filters where only those that pass the is_valid check make it through. This filtered set of Items is then passed to a Batcher which breaks the Items into groups called Batches. Batches will be executed sequentially as independent changes going through a multi-step process. First, the Batch goes to a Transformer which makes the actual changes to the codebase. At this point, some Commands that have run_pre_validation set to true may run, handling things like code generation or formatting. Next, Validators are invoked which check to ensure the codebase is still healthy. After this, remaining Commands are run which perform post-change processing. Finally, the Repo object will check for changes, commit them if present, and submit them (i.e. as a Pull Request). Once this is done, the Repo object will return the repository to a clean state in preparation for the next Batch.

## **Scheduled Runs**

AutoTransform provides a scheduling component for setting up automatically scheduled runs to maintain a codebase in to the future. Once set up, scheduled runs will ensure that an organization's codebase stays up-to-date.

### **Schedule File**

To get scheduled runs going, a JSON file with all scheduling information is required. The schedule format looks like the following:
```
{
    "base_time": <int>,
    "runner": {
        "type": <RunnerType>,
        "params": {
            ...
        }
    },
    "excluded_days": [<0-6>],
    "schemas": [
        {
            "type": <builder, file>,
            "schema": <string>,
            "schedule": {
                "repeats": <daily, weekly>,
                "hour_of_day": <0-23>,
                "day_of_week": <0-6>,
                "sharding": {
                    "num_shards": <int>,
                    "shard_filter": {
                        "type": FilterType,
                        "params": {
                            ...
                        }
                    }
                }
            }
        }
    ]
}
```
To see an example, check out `data/autotransform_schedule.json`.

### **Scheduling Params**

The following params are used when scheduling schemas to run automatically.
  * **Overall Params**
    * **base_time**: This serves as the basis for determining hour of day and day of week. When scheduling is invoked, this time is subtracted from the current time to determine day of week and hour of day, with the base time treated as hour 0 on day 0.
    * **runner**: This is an encoded runner object. All schemas that have been scheduled will be run using this object. It should trigger runs on the organization's CI infrastructure.
    * **excluded_days**: A list of days of the week that schemas will not run. Defaults to empty.
    * **schemas**: A list of schemas that are automatically scheduled.
  * **Schema Params**
    * **type**: Either the string "builder" or the string "file". This is used to determine whether the value of the schema param refers to a SchemaBuilderType or a file path.
    * **schema**: Either a SchemaBuilderType or a file path.
    * **Schedule**
      * **repeats**: Either the string "daily" or the string "weekly". How often the schema will be run.
      * **hour_of_day**: Which hour of the day, using the logic described for base_time, that the schema will be run. Defaults to 0.
      * **day_of_week**: Which day of the week, using the logic described for base_time, that the schema will be run. Defaults to 0. Only applies to weekly runs.
      * **Sharding**: A Sharded schema is run on a subset of it's input each time it is run. This subset is determined by the sharding params and can be used to break large runs over a codebase in to smaller pieces. Optional to include.
        * **num_shards**: The total number of shards to spread the input across.
        * **shard_filter**: A ShardFilter object that will be used to perform the actual sharding. It will get the num_shards and current_shard from the scheduler when constructed.

### **Invoking Scheduled Runs**

Scheduled runs are invoked using `autotransform schedule <path_to_schedule_file>`. If you use Github, you can see an example workflow at `data/workflows/autotransform_scheduler.yml` that shows how to use Github actions for automating scheduled runs. If you do not use Github, you can set up a cron job on your organization's infrastructure to invoke the script on a schedule. Additionally, the `--time=<int>` option can be used to override the current timestamp when calculating hour/day. Using this may be useful if there is potential delay in your automation infrastructure.

As a note, if using GithubActions, the github_token used must have admin access to the repo to trigger further github actions.

## Managing Changes

AutoTransform provides a managing command for managing outstanding Changes, updating, merging, abandoning, and handling other actions for outstanding Changes.

### Manager File

To manage outstanding Changes, a JSON file with all manager information is required. The manage format looks like the following:
```
{
    "repo": {
        "type": <RepoType>,
        "params": {
            ...
        }
    },
    "runner": {
        "type": <RunnerType>,
        "params": {
            ...
        }
    },
    "steps": [
        {
            "type": <StepType>,
            "params": {
                ...
            }
        },
        ...
    ]

}
```
To see an example, check out `data/autotransform_manage.json`.

### Managing Params

* **Repo**: The Repo to fetch outstanding Changes for.
* **Runner**: The Runner to use for updating outstanding Changes.
* **Steps**: The Steps to check against the outstanding Changes.

### **Invoking Management**

Management is invoked using `autotransform manage <path_to_manager_file>`. If you use Github, you can see an example workflow at `data/workflows/autotransform_manager.yml` that shows how to use Github actions for automating manager runs. If you do not use Github, you can set up a cron job on your organization's infrastructure to invoke the script on a schedule.

As a note, if using GithubActions, the github_token used must have admin access to the repo to trigger further github actions.

## **Schema Components**

The core of AutoTransform is the [schema](https://github.com/nathro/AutoTransform/blob/master/autotransform/schema/schema.py). A schema is a collection of components and configurations required to actually execute a change.

* **[Config](https://github.com/nathro/AutoTransform/blob/master/autotransform/schema/config.py)**
    * **Name** - A unique name to identify the change in PRs and scheduling
    * **Owner** - An owner to notify about actions taken by the schema
    * **Allowed Validation Level** - The level of validation errors allowed by the schema (none vs warning vs error)
* **[Input](https://github.com/nathro/AutoTransform/blob/master/autotransform/input/base.py)** - The input component returns a list of Items that are potential targets of the change (i.e. file paths)
* **[Filters](https://github.com/nathro/AutoTransform/blob/master/autotransform/filter/base.py)** - Filters take a set of Items and apply criteria to the Items that were not applied by the Input, such as checking if the key of the item matches a regex pattern.
* **[Batcher](https://github.com/nathro/AutoTransform/blob/master/autotransform/batcher/base.py)** - A batcher takes a set of filtered Items and breaks them into groups that can be executed independently. This component also generates metadata for this grouping used for things like the body of a pull request.
* **[Transformer](https://github.com/nathro/AutoTransform/blob/master/autotransform/transformer/base.py)** - The core of any change, takes a batch and actually makes changes to files based on the batch provided.
* **[Validators](https://github.com/nathro/AutoTransform/blob/master/autotransform/validator/base.py)** - Validators are run after transformation to check the health of a codebase after the transformation and ensure no issues are present. Things like typing, testing, etc...
* **[Commands](https://github.com/nathro/AutoTransform/blob/master/autotransform/command/base.py)** - Post run processes that need to be executed. Could involve updating databases, generating code, etc...
* **[Repo](https://github.com/nathro/AutoTransform/blob/master/autotransform/repo/base.py)** - An abstraction for the repository being modified. Allows functionality like commits or submitting changes for review.

## **Code Review Components**

* **[Change](https://github.com/nathro/AutoTransform/blob/master/autotransform/change/base.py)** - A Change represents a submission to a code review and/or source control system. They are used by AutoTransform to manage these submissions to do things like land approved code, abandon stale changes, etc...

* **[Step](https://github.com/nathro/AutoTransform/blob/master/autotransform/step/base.py)** - A Step is used by AutoTransform to determine what actions to take for a given Change. They evaluate criteria and determine what should be done for handling an outstanding Change. Most Step logic can be handled through the use of the ConditionalStep, requiring only the creation of new Conditions.

## **Other Components**

* **[Config Fetcher](https://github.com/nathro/AutoTransform/blob/master/autotransform/config/fetcher.py)** - The ConfigFetcher allows for configuration of AutoTransform as a whole. This includes things like specifying custom component imports as well as providing credentials, such as a github token. There are three config fetchers provided as part of AutoTransform that can be selected based on the AUTO_TRANSFORM_CONFIG environment variable:
    * **[Default](https://github.com/nathro/AutoTransform/blob/master/autotransform/config/default.py)** - Pulls configuration from autotransform/config/config.ini, a [sample_config.ini](https://github.com/nathro/AutoTransform/blob/master/autotransform/config/sample_config.ini) file provides an example. This is the easiest choice for local use cases on a developers machine.
    * **[Environment Variable](https://github.com/nathro/AutoTransform/blob/master/autotransform/config/envvar.py)** - Pulls configuration from environment variables, using names that match the pattern: AUTO_TRANSFORM_&lt;SECTION>_&lt;SETTING> where section and setting represent the section and setting that would be used in a config.ini file, such as AUTO_TRANSFORM_CREDENTIALS_GITHUB_TOKEN. This is the preferred option for production use cases.
* **[Item](https://github.com/nathro/AutoTransform/blob/master/autotransform/item/base.py)** - An item represents a potential input to a transformation. It can represent a file or any other logical object. All Items must have keys that uniquely identify them within their type. While items of different types can have
the same key, separate items of the same type must have unique keys. Subclasses of Item can provide utility functionality, or support strongly typed extra data.
* **[Runner](https://github.com/nathro/AutoTransform/blob/master/autotransform/runner/base.py)** - Runner components are used to trigger a run of AutoTransform either locally or on an organization's remote infrastructure or job queue system. This allows organizations to set up integrations with their infrastructure to speed up developers by offloading the runs of AutoTransform. Additionally, remote infrastructure is used by scheduling logic when setting up scheduled runs of AutoTransform.

# **Upcoming Milestones**

## **Milestone 1 - Beta 0.2.0 - ETA 5/29/2022**

An early beta with all core functionality, including scheduling and change management available with an initial set of core components. This represents a mostly locked down version of the code, APIs, etc. Breaking changes may still happen after this release, but they will be weighted heavily against potential existing adoption. Before this release, breaking changes will be far more likely.

## **Milestone 2 - Release 1.0.0 - ETA 7/29/2022**

This will include changes made as part of easing initial deployments. At this point AutoTransform will have been deployed to a production environment and the components will be considered production ready. Breaking changes after this release will be very unlikely and will coincide with new major versions of AutoTransform.

# **Security Best Practices**

The nature of AutoTransform creates the potential for significant security implications when deployed at an organization. Because of this, there is a set of best practices that are strongly encouraged to ensure security is maintained. These are less important for individual work that doesn’t get deployed to a production environment (i.e. updating personal projects).

## **AutoTransform User**

Create a separate user in whatever code review/management system (i.e. Github) you use that will be the actor for all changes/management and supply their credentials via secrets/environment variables. Try to minimize access to these credentials using things like Github repo secrets. The number of people capable of creating bot credentials should be as small a set as possible.

## **Reviewed Components**

All custom components used should be required to pull from a repo/package that goes through a code review process or is otherwise from a trusted open source provider (i.e. AutoTransform’s core components). Components will be able to access credentials and make changes to the codebase and thus must be reviewed.

## **Checked In Schemas**

All schemas that are run through scheduling must be checked into the codebase. This prevents people from stitching together components in unexpected ways that can present security or codebase health concerns. By ensuring all schemas are checked in you additionally ensure that schemas are all reviewed.

## **Thorough Review**

Schemas and components should be thoroughly reviewed and tested by people familiar with what they are trying to accomplish. Automated changes are readily accepted by developers and it is crucial that the schemas that produce these changes can be trusted. By putting in the upfront time to review the schemas, the review of the changes can be made much easier (or even unnecessary).

# **Schema Best Practices**

## **Batch Correctly**

The batching method chosen is very important. The more thorough reviewers need to be, the smaller the batches should be. If a schema can be guaranteed correct, one batch is fine. If review of each change is needed, the changes should be made in to small batches.

## **No Mixing Of Safety Categories**

Some schemas produce guaranteed safe changes, some schemas produce mostly safe, but potentially incorrect changes. Separate schemas should be created for each of these types of changes. Mixing these types of changes in one schema will lead to complacency in review that can let errors slip through.

## **Test Test Test**

Every component and schema should be thoroughly tested for each different possible case. AutoTransform is a scaling system that requires an upfront investment in exchange for automating all future work. By thoroughly testing your components and schemas you support all future changes.

## **Mind Developer Time**

Just because something can be automated to be made better, doesn’t mean it should be. Developer time is important and wasting it by submitting numerous of changes for review that don’t really do much to improve things is a bad practice that can eliminate the benefits of AutoTransform. Try to minimize review required for changes where possible, and if review is required, ensure that it is worth the time of the reviewer to get the changes in.

## **Create A Council**

As developers in your organization learn about AutoTransform, they will inevitably want to use it. Growth of usage will likely be organic and rapid, including many people without a lot of experience using these types of tools. Be prepared to have a council or other group these developers can go to for support.