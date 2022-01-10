# AutoTransform

AutoTransform is a structured, schema based approach to large scale code modification. It provides a structure for designing and implementing these types of modifications using common components that can be utilized to accelerate development.

### Example Use Cases

Here is a short, non-exhaustive list of potential use cases.

 - **Library owners**: Updates to libraries might break existing uses due to changes in API. As part of these updates, you can release transformations that will bring existing uses in line with your updates
 - **Language developers**: Much like libraries, changes to languages can release new features or functionality with improved performance characteristics. Transformations can be developed to ease adoption of these new features.
 - **Codebase Maintainance**: Maintaining large codebases can be cumbersome, setting up automated transformations for things like lint/format/style issues can allow easier, automated maintainance of your codebase.
 - **Deprecation**: Deprecating existing things (such as experimental features) can be done safely and automatically through setting up transformations.

Any time someone is writing repetitive code, AutoTransform can help. It can be your most productive developer!

### Installing

> **⚠ WARNING:** AutoTransform requires Python 3.10

 - **Latest Release** `pip install AutoTransform`
 - **Bleeding Edge** `pip install git+git://github.com/nathro/AutoTransform.git`
   - Windows users may need to replace `git://` with `https://`
   - If you do not have git use: `pip install https://github.com/nathro/AutoTransform/archive/master.zip`

### Components

AutoTransform schemas are structured around a set of components that define the transformation. These components are:
 - **Input**: Gets all eligible files for transformation
 - **Filters**: Filters down eligible files based on each Filter's criteria
 - **Batcher**: Breaks a set of files in to logical groupings with metadata
 - **Transformer**: Performs actual transformations on the batches
 - **Validators**: Performs post transformation validation to ensure code is valid (i.e. tests pass)
 - **Commands**: Performs any post transformation processing required (i.e. running a build/code generation suite)
 - **Repo**: Controls all interaction with the version control/code review system
 - **Config**: Stores all configuration options for the schema, such as what level of validation issues are allowed

Components are located within subpackages named for them (i.e. `autotransform.batcher`). Explore these packages either in source or through the interpreter to discover available components and the parameters they use. If you need components that do not exist check out CONTRIBUTING.md or CUSTOM_DEPLOYMENT.md

### Configuration

In addition to schema configuration, configuration is available for AutoTransform as a whole to provide things like credentials for github. The default configuration is pulled from data/config.ini, see data/sample_config.ini for the configuration format. Other configuration options are available using the environment vairable `AUTO_TRANSFORM_CONFIG` (see `autotransform.config`).

### Scripts

AutoTransform exposes two scripts as part of package deployment
 - autotransform.regexmod is exposed as `regexmod` run `regexmod -h` for options
 - autotransform.manager is exposed as `atmanager` run `atmanager -h` for options