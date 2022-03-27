# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""A simple script for running regex based transformations from the command line."""

import argparse
import time

from autotransform.batcher.single import SingleBatcher
from autotransform.filter.extension import ExtensionFilter
from autotransform.input.directory import DirectoryInput
from autotransform.repo.git import GitRepo
from autotransform.repo.github import GithubRepo
from autotransform.schema.schema import AutoTransformSchema
from autotransform.transformer.regex import RegexTransformer
from autotransform.worker.coordinator import Coordinator
from autotransform.worker.local import LocalWorker


def parse_arguments() -> argparse.Namespace:
    """Parses the script arguments. Run with -h to see all arguments.

    Returns:
        argparse.Namespace: The arguments for the regexmod
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
        "--git",
        metavar="git_repo_path",
        type=str,
        required=False,
        help="The absolute path to a git repo containing the directory. Setting this will cause "
        + "changes to be commited to git.",
    )
    parser.add_argument(
        "--github",
        metavar="repo_name",
        type=str,
        required=False,
        help="The full name of the github repo that a pull request should be submitted against",
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
        "--summary",
        metavar="summary",
        type=str,
        required=False,
        default="",
        help="The summary to include in the pull request when using github",
    )
    parser.add_argument(
        "--tests",
        metavar="tests",
        type=str,
        required=False,
        default="",
        help="The text of a tests section of a pull request body",
    )
    return parser.parse_args()


def main():
    """Run the regex based transformation."""
    args = parse_arguments()
    inp = DirectoryInput({"path": args.directory})
    transformer = RegexTransformer({"pattern": args.pattern, "replacement": args.replacement})
    batcher = SingleBatcher(
        {"metadata": {"title": args.title, "summary": args.summary, "tests": args.tests}}
    )
    filters = []
    extensions = args.extensions
    if isinstance(extensions, str):
        extensions = extensions.split(",")
        extensions = [
            extension if extension.startswith(".") else "." + extension for extension in extensions
        ]
        filters.append(ExtensionFilter({"extensions": extensions}))

    git_repo = args.git
    if isinstance(git_repo, str):
        github_repo = args.github
        if isinstance(github_repo, str):
            print("Using Github repo: " + github_repo)
            print("Local repo: " + git_repo)
            repo = GithubRepo({"path": git_repo, "full_github_name": github_repo})
        else:
            print("Using git repo: " + git_repo)
            repo = GitRepo({"path": git_repo})
    else:
        repo = None
    schema = AutoTransformSchema(inp, batcher, transformer, filters=filters, repo=repo)
    coordinator = Coordinator(schema, LocalWorker)
    start_time = time.time()
    coordinator.start()
    timeout = 30
    while not coordinator.is_finished() and time.time() <= start_time + timeout:
        time.sleep(1)
    coordinator.kill()


if __name__ == "__main__":
    main()
