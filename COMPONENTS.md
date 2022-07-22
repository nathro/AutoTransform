# **Components**

### **Data Flow**

**[A visual representation](https://lucid.app/lucidchart/eca43a3d-175f-416f-bb4f-4363d56f951b/edit?invitationId=inv_f44ed708-8c4a-4998-96f2-8b860aba8ebc)**

The Input component of the schema will get a list of Items that may serve as inputs to a transformation, these are then passed through the Filters where only those that pass the is_valid check make it through. This filtered set of Items is then passed to a Batcher which breaks the Items into groups called Batches. Batches will be executed sequentially as independent changes going through a multi-step process. First, the Batch goes to a Transformer which makes the actual changes to the codebase. At this point, some Commands that have run_pre_validation set to true may run, handling things like code generation or formatting. Next, Validators are invoked which check to ensure the codebase is still healthy. After this, the remaining Commands are run which perform post-change processing. Finally, the Repo object will check for changes, commit them if present, and submit them (i.e. as a Pull Request). Once this is done, the Repo object will return the repository to a clean state in preparation for the next Batch.

### **Schema Components**

The core of AutoTransform is the [schema](https://github.com/nathro/AutoTransform/blob/master/src/python/autotransform/schema/schema.py). A schema is a collection of components and configurations required to actually execute a change.

* **[Config](https://github.com/nathro/AutoTransform/blob/master/src/python/autotransform/schema/config.py)**
    * **Schema Name** - A unique name to identify the Schema
    * **Owners** - A list of owners responsible for the Schema
    * **Allowed Validation Level** - The level of validation errors allowed by the schema (none vs warning vs error)
* **[Input](https://github.com/nathro/AutoTransform/blob/master/src/python/autotransform/input/base.py)** - The input component returns a list of Items that are potential targets of a change (i.e. file paths)
* **[Filters](https://github.com/nathro/AutoTransform/blob/master/src/python/autotransform/filter/base.py)** - Filters take a set of Items and apply criteria to the Items that were not applied by the Input, such as checking if the key of the item matches a regex pattern.
* **[Batcher](https://github.com/nathro/AutoTransform/blob/master/src/python/autotransform/batcher/base.py)** - A batcher takes a set of filtered Items and breaks them into groups that can be executed independently. This component also generates metadata for this grouping used for things like the body of a pull request.
* **[Transformer](https://github.com/nathro/AutoTransform/blob/master/src/python/autotransform/transformer/base.py)** - The core of any change, takes a batch and actually makes changes to files based on the batch provided.
* **[Validators](https://github.com/nathro/AutoTransform/blob/master/src/python/autotransform/validator/base.py)** - Validators are run after transformation to check the health of a codebase after the transformation and ensure no issues are present. Things like typing, testing, etc...
* **[Commands](https://github.com/nathro/AutoTransform/blob/master/src/python/autotransform/command/base.py)** - Post transformation processes that need to be executed. Could involve updating databases, generating code, etc...
* **[Repo](https://github.com/nathro/AutoTransform/blob/master/src/python/autotransform/repo/base.py)** - An abstraction for the repository being modified. Allows functionality like commits or submitting changes for review.

### **Code Review Components**

* **[Change](https://github.com/nathro/AutoTransform/blob/master/src/python/autotransform/change/base.py)** - A Change represents a submission to a code review and/or source control system. They are used by AutoTransform to manage these submissions to do things like land approved code, abandon stale changes, etc...

* **[Step](https://github.com/nathro/AutoTransform/blob/master/src/python/autotransform/step/base.py)** - A Step is used by AutoTransform to determine what Actions to take for a given Change. They evaluate criteria and determine what should be done for handling an outstanding Change. Most Step logic can be handled through the use of the ConditionalStep, requiring only the creation of new Conditions.

### **Other Components**

* **[Config Fetcher](https://github.com/nathro/AutoTransform/blob/master/src/python/autotransform/config/fetcher.py)** - The ConfigFetcher allows for configuration of AutoTransform as a whole. This includes things like specifying custom component imports as well as providing credentials, such as a github token. There are two config fetchers provided as part of AutoTransform that can be selected based on the AUTO_TRANSFORM_CONFIG environment variable:
    * **[Default](https://github.com/nathro/AutoTransform/blob/master/src/python/autotransform/config/default.py)** - Pulls configuration from config.json files. This is the easiest choice for local use cases on a developers machine. The files used will be a config.json file in the `autotransform-config` package itself, a config relative to the root of a git repo if inside one `{repo}/autotransform/config.json`, and a config relative to the current working directory `{cwd}/autotransform/config.json`. The relative path of the repo and cwd configs can be specified by environment variables `AUTO_TRANSFORM_(REPO/CWD)_CONFIG_PATH`. Settings duplicated across files will prefer cwd configs to repo configs to package configs.
    * **[Environment](https://github.com/nathro/AutoTransform/blob/master/src/python/autotransform/config/environment.py)** - Pulls configuration from environment variables, using names that match the pattern: `AUTO_TRANSFORM_<SETTING>` where setting represents the setting that would be used in a config.json file, such as `AUTO_TRANSFORM_GITHUB_TOKEN`. This is the preferred option for production use cases.
    * **Custom** - A custom ConfigFetcher can be used by setting `AUTO_TRANSFORM_CONFIG` to a JSON encoding of `{class_name: <The name of a class extending ConfigFetcher>, module: <the fully qualified module where the class exists>, data: <A dictionary containing any data needed to instantiate the fetcher>}`
* **[Item](https://github.com/nathro/AutoTransform/blob/master/src/python/autotransform/item/base.py)** - An item represents a potential input to a transformation. It can represent a file or any other logical object. All Items must have keys that uniquely identify them within their type. While items of different types can have the same key, separate items of the same type must have unique keys. Subclasses of Item can provide utility functionality, or support strongly typed extra data.
* **[Runner](https://github.com/nathro/AutoTransform/blob/master/src/python/autotransform/runner/base.py)** - Runner components are used to trigger a run of AutoTransform either locally or on an organization's remote infrastructure or job queue system. This allows organizations to set up integrations with their infrastructure to speed up developers by offloading the runs of AutoTransform. Additionally, remote infrastructure is used by scheduling logic when setting up scheduled runs of AutoTransform.