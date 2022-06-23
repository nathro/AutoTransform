# **Overview**

Full documentation available [here](https://autotransform.readthedocs.io)

## **Installing**

> **⚠ WARNING:** AutoTransform requires Python 3.10

 - **Latest Release** `pip install AutoTransform`
 - **Bleeding Edge** `pip install git+git://github.com/nathro/AutoTransform.git`
   - Windows users may need to replace `git://` with `https://`

After installing via pip, AutoTransform can be initialized using `autotransform init`. If called within a git repo, this script will also initialize the repo to use AutoTransform. For a simple setup experience, run `autotransform init --simple --github` or `autotransform init --simple --no-github`
## **Summary**

AutoTransform is an opensource framework for large-scale code modification. It enables a schema-based system of defining codemods that can then be run using AutoTransform, with options for automatic scheduling as well as change management. AutoTransform leverages a component-based model that allows adopters to quickly and easily get whatever behavior they need through the creation of new, custom components. Additionally, custom components can readily be added to the component library of AutoTransform to be shared more widely with others using the framework.

## **Goal**

The goal of AutoTransform is to make codebase modification simple, easy, and automatic. By providing a clear structure for definition, all types of modifications can be automated. Some examples include:

* Library upgrades
* API changes
* Performance improvements
* Lint or style fixes
* Unused code
* One-off refactors
* Any other programmatically definable modification

## **Philosophies**

There are a core set of philosphies that guide AutoTransform's development. These drive decisions around functionality, implementation details, and best practies.

### **Components Are Best**

AutoTransform heavily uses a component based model for functionality. This allows easy customization through the creation of new plug-and-play components. Core logic is about funneling information between components, while the components themselves contain business logic. While AutoTransform provides an ever-growing library of components for ease of adoption, bespoke components will always be needed for some use cases.

### **Support All Languages**

AutoTransform, though written in Python, is a language agnostic framework. Our component model allows AutoTransform to treat each component as a black-box that can leverage whatever tooling or language makes sense for the goal of the component. This is most heavily needed for the components which actually make code changes where leveraging tools for Abstract(or Concrete) Syntax Trees(AST/CST) is often done in the language being modified.

### **Value Developer Time**

Managing large scale changes can be extremely time consuming, AutoTransform puts automation first with the goal of automating as much of the process as possible. Developer time is incredibly valuable and should be saved for things that actually require it. If a computer can do it, a computer should do it.

## **Example - Typing**

As an example of how AutoTransform might be used, let’s go through the case of typing a legacy codebase. This is a notoriously difficult and time consuming process.

### **Static Inference**

A codemod can be written that statically infers types from the types around whatever needs typing. Hooking this up to scheduled runs would mean that as people type your code, other types can later be inferred. Additionally, as the codemod types code, that can reveal further types that can be statically inferred. This would allow typing to slowly build up over time automatically as the codemod runs and developers introduce more types themselves, significantly speeding up the process of typing a legacy codebase.

### **Run Time Logging**

In addition to static typing, a codemod could instrument untyped functions or other code to log types at run time. These logs could then be fed into the codemod to add types to code that can’t be inferred but can be determined at run time. This codemod could additionally be written to only instrument a small part of the codebase at a given time, preventing excessive resource utilization.

### **The Whole Versus the Sum of the Parts**

Each codemod that can change code can benefit from all other codemods. As run time logging adds types, static inference can make better changes. Dead code removal can clean up untyped code. The layered passes, and building on top of the changes of each codemod, can produce significantly greater wins.