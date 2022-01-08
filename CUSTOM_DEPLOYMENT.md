# Extending For Your Organization

AutoTransform is a generic framework for defining automated code transformations, but may not provide all components needed by your specific organization. Fret not, AutoTransform is built to be extended!

If you are looking to deploy AutoTransform for your organization, simply fork the AutoTransform repo and make your changes as needed. To support this type of extending, sections have been added to the source intended to hold the imports, getters, and types required for creating bespoke components. See `autotransform.batcher.type` and `autotransform.batcher.factory` for examples. Additionally configuration fetching can be customized, see `autotransform.config` for how.

When adding new components to AutoTransform that are specific to your organization, the expected pattern is to put them in the `autotransform.<organization>.<component>` package where organization is the name of your organization (i.e. `microsoft`) and component is the type of component being added (i.e. `batcher`). All other bespoke modules/subpackages should live within `autotransform.<organization>`. Following these practices will reduce the risk of conflicts when merging upstream changes in to your deployment.

