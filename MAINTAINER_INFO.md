# Maintainer Info

This info is for repo maintainers and not needed for general audiences.

### Merging Pull Requests/Features

When a new feature/pull request is merged in to master, always merge with `--no-ff` to preserve feature history. Additionally, the commit that merges the feature should update the changelog for the upcomming release so no features are missed or have to be added later. If possible include links to the associated pull request/issue/etc... with the changelog.

If an upgrade package is associated with a change, include information for downloading the package in the changelog so that bespoke deployments can more readily move to new releases.

### Branches

 - master: Points to the current development state. This is the bleeding edge of AutoTransform
 - release: Points to the most recently released version on PyPi

### Release Process

Steps to release AutoTransform
 - Checkout the current master from Github
 - Ensure source in good shape
   - `py -m mypy autotransform`
   - `py -m pytest tests/`
   - `py -m pylint autotransform --enable=W0611,R0201,R0902,R0903,R0913,R1732 --disable=R0801`
 - Validate changelog accurate and add summary
 - Bump version in setup.py, update version in changelog for release
 - Commit version bump with message Release-&lt;version&gt;
 - `py -m build`
 - `py -m twine upload --repository pypi dist/AutoTransform-<version>*`
 - Update release branch to point to master
 - Push changes upstream
 - Add new release and tag to Github repo (tag should be "Release-&lt;version&gt;")
 - Switch to master branch
 - Add new sections to Change Log file for next release
   - Main title = Upcoming Release
   - New Components
   - New Scripts
   - API Changes
   - Upgrade Packages
   - Misc
 - Commit as "Post Release-&lt;version&gt; Preparation For Next Release"
 - Push upstream