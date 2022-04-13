# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""A simple script for running regex based transformations from the command line."""

import argparse
import json
import time

from autotransform.batcher.single import SingleBatcher
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.event.run import ScriptRunEvent
from autotransform.filter.extension import ExtensionFilter
from autotransform.input.directory import DirectoryInput
from autotransform.repo.git import GitRepo
from autotransform.repo.github import GithubRepo
from autotransform.schema.schema import AutoTransformSchema
from autotransform.transformer.regex import RegexTransformer
from autotransform.worker.coordinator import Coordinator
from autotransform.worker.local import LocalWorker


def parse_arguments() -> argparse.Namespace:
    """Sets up the argparser for the regexmod script and parses the arguments.

    Returns:
        argparse.Namespace: The arguments for the regexmod.
    """
    parser = argparse.ArgumentParser(description="Runs simple regex based codemods")

    # Filter Arguments
    parser.add_argument(
        "-e",
        "--extensions",
        metavar="extensions",
        type=str,
        required=False,
        help="A comma separated list of extensions for files to modify",
    )

    # Repo Arguments
    parser.add_argument(
        "--github",
        metavar="repo_name",
        type=str,
        required=False,
        help="The full name of the github repo that a pull request should be submitted against",
    )
    parser.add_argument(
        "--branch",
        metavar="branch",
        type=str,
        required=False,
        help="The base branch to use for git, needed for any git changes",
    )

    # Input Arguments
    parser.add_argument(
        "directory",
        metavar="directory",
        type=str,
        help="The directory to search within for files to modify",
    )

    # Transformation Arguments
    parser.add_argument("pattern", metavar="pattern", type=str, help="The pattern to be replaced")
    parser.add_argument(
        "replacement", metavar="replacement", type=str, help="What you wish to replace with"
    )

    # Arguments used by the repo object for committing/PRs
    parser.add_argument(
        "--title",
        metavar="title",
        type=str,
        required=False,
        default="",
        help="The message for any git commit and the title of any github pull request",
    )
    parser.add_argument(
        "--body",
        metavar="body",
        type=str,
        required=False,
        default="",
        help="The body to include in the pull request when using github",
    )
    return parser.parse_args()


def main():
    """Run the regex based transformation."""
    event_args = {}
    event_handler = EventHandler.get()
    args = parse_arguments()

    # Get the input component
    inp = DirectoryInput({"path": args.directory})
    event_args["directory"] = args.directory
    event_handler.handle(DebugEvent({"message": f"Dirctory: {args.directory}"}))

    # Get the transformer component
    transformer = RegexTransformer({"pattern": args.pattern, "replacement": args.replacement})
    event_handler.handle(
        DebugEvent({"message": f"Pattern: {args.pattern} -- Replacement: {args.replacement}"})
    )
    event_args["pattern"] = args.pattern
    event_args["replacement"] = args.replacement

    # Get the batcher
    batcher = SingleBatcher({"metadata": {"title": args.title, "body": args.body}})
    if args.title is not None:
        event_handler.handle(DebugEvent({"message": f"Commit Title: {args.title}"}))
        event_args["title"] = args.title
    if args.body is not None:
        event_handler.handle(DebugEvent({"message": f"PR Body: {args.body}"}))
        event_args["body"] = args.body

    # Get the extensions to use for an extension filter
    filters = []
    extensions = args.extensions
    if isinstance(extensions, str):
        extensions = extensions.split(",")
        extensions = [
            extension if extension.startswith(".") else "." + extension for extension in extensions
        ]
        event_args["extensions"] = json.dumps(extensions)
        event_handler.handle(DebugEvent({"message": f"Extensions: {json.dumps(extensions)}"}))
        filters.append(ExtensionFilter({"extensions": extensions}))

    # Get the repo component, using the git branch and the github name from args if present
    git_branch = args.branch
    if isinstance(git_branch, str):
        event_args["branch"] = git_branch
        event_handler.handle(DebugEvent({"message": f"Git Base Branch: {git_branch}"}))
        github_repo = args.github
        if isinstance(github_repo, str):
            event_args["github_repo"] = github_repo
            event_handler.handle(DebugEvent({"message": f"Github Repo Name: {github_repo}"}))
            repo = GithubRepo({"base_branch_name": git_branch, "full_github_name": github_repo})
        else:
            repo = GitRepo({"base_branch_name": git_branch})
    else:
        repo = None

    # Construct and run the schema
    event_handler.handle(ScriptRunEvent({"script": "regexmod", "args": event_args}))
    schema = AutoTransformSchema(inp, batcher, transformer, filters=filters, repo=repo)
    coordinator = Coordinator(schema, LocalWorker)
    start_time = time.time()
    coordinator.start()
    timeout = 60
    while not coordinator.is_finished() and time.time() <= start_time + timeout:
        time.sleep(1)
    coordinator.kill()


if __name__ == "__main__":
    main()
