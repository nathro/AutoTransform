# **Best Practices**
## **Security Best Practices**

The nature of AutoTransform creates the potential for significant security implications when deployed at an organization. Because of this, there is a set of best practices that are strongly encouraged to ensure security is maintained. These are less important for individual work that doesn’t get deployed to a production environment (i.e. updating personal projects).

### **AutoTransform User**

Create a separate user in whatever code review/management system (i.e. Github) you use that will be the actor for all changes/management and supply their credentials via secrets/environment variables. Try to minimize access to these credentials using things like Github repo secrets. The number of people capable of creating bot credentials should be as small a set as possible.

### **Reviewed Components**

All custom components used should be required to pull from a repo/package that goes through a code review process or is otherwise from a trusted open source provider (i.e. AutoTransform’s core components). Components will be able to access credentials and make changes to the codebase and thus must be reviewed.

### **Checked In Schemas**

All schemas that are run through scheduling must be checked into the codebase. This prevents people from stitching together components in unexpected ways that can present security or codebase health concerns. By ensuring all schemas are checked in you additionally ensure that schemas are all reviewed.

### **Thorough Review**

Schemas and components should be thoroughly reviewed and tested by people familiar with what they are trying to accomplish. Automated changes are readily accepted by developers and it is crucial that the schemas that produce these changes can be trusted. By putting in the upfront time to review the schemas, the review of the changes can be made much easier (or even unnecessary).

## **Schema Best Practices**

### **Batch Correctly**

The batching method chosen is very important. The more thorough reviewers need to be, the smaller the batches should be. If a schema can be guaranteed correct, one batch is fine. If review of each change is needed, the changes should be made in to small batches.

### **No Mixing Of Safety Categories**

Some schemas produce guaranteed safe changes, some schemas produce mostly safe, but potentially incorrect changes. Separate schemas should be created for each of these types of changes. Mixing these types of changes in one schema will lead to complacency in review that can let errors slip through.

### **Test Test Test**

Every component and schema should be thoroughly tested for each different possible case. AutoTransform is a scaling system that requires an upfront investment in exchange for automating all future work. By thoroughly testing your components and schemas you support all future changes.

### **Mind Developer Time**

Just because something can be automated to be made better, doesn’t mean it should be. Developer time is important and wasting it by submitting numerous changes for review that don’t really do much to improve things is a bad practice that can eliminate the benefits of AutoTransform. Try to minimize review required for changes where possible, and if review is required, ensure that it is worth the time of the reviewer to get the changes in.

### **Create A Council**

As developers in your organization learn about AutoTransform, they will inevitably want to use it. Growth of usage will likely be organic and rapid, including many people without a lot of experience using these types of tools. Be prepared to have a council or other group these developers can go to for support.