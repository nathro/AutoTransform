# **Overview**

Full documentation available [here](https://autotransform.readthedocs.io)

## **Installing**

> **⚠ WARNING:** AutoTransform requires Python 3.10

 - **Latest Release** `pip install AutoTransform`
 - **Bleeding Edge** `pip install git+git://github.com/nathro/AutoTransform.git`
   - Windows users may need to replace `git://` with `https://`
   - If you do not have git use: `pip install https://github.com/nathro/AutoTransform/archive/master.zip`

After installing via pip, AutoTransform can be initialized using `autotransform init`. If called within a git repo, this script will also initialize the repo to use AutoTransform. For a simple setup experience, run `autotransform init --simple --github` or `autotransform init --simple --no-github`
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
    * **[Default](https://github.com/nathro/AutoTransform/blob/master/autotransform/config/default.py)** - Pulls configuration from config.ini files, a [sample_config.ini](https://github.com/nathro/AutoTransform/blob/master/autotransform/config/sample_config.ini) file provides an example. This is the easiest choice for local use cases on a developers machine. The files used will be a config.ini file in the `autotransform/config` package itself, a config relative to the root of a git repo if inside one `{repo}/autotransform/config.ini`, and a config relative to the current working directory `{cwd}/autotransform/config.ini`. The relative path of the repo and cwd configs can be specified by environment variables `AUTO_TRANSFORM_(REPO/CWD)_CONFIG_PATH`. Settings duplicated across files will prefer cwd configs to repo configs to package configs.
    * **[Environment Variable](https://github.com/nathro/AutoTransform/blob/master/autotransform/config/envvar.py)** - Pulls configuration from environment variables, using names that match the pattern: `AUTO_TRANSFORM_<SECTION>_<SETTING>` where section and setting represent the section and setting that would be used in a config.ini file, such as `AUTO_TRANSFORM_CREDENTIALS_GITHUB_TOKEN`. This is the preferred option for production use cases.
* **[Item](https://github.com/nathro/AutoTransform/blob/master/autotransform/item/base.py)** - An item represents a potential input to a transformation. It can represent a file or any other logical object. All Items must have keys that uniquely identify them within their type. While items of different types can have
the same key, separate items of the same type must have unique keys. Subclasses of Item can provide utility functionality, or support strongly typed extra data.
* **[Runner](https://github.com/nathro/AutoTransform/blob/master/autotransform/runner/base.py)** - Runner components are used to trigger a run of AutoTransform either locally or on an organization's remote infrastructure or job queue system. This allows organizations to set up integrations with their infrastructure to speed up developers by offloading the runs of AutoTransform. Additionally, remote infrastructure is used by scheduling logic when setting up scheduled runs of AutoTransform.