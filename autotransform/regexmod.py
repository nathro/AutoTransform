# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import argparse
import time

from autotransform.batcher.single import SingleBatcher
from autotransform.common.package import AutoTransformPackage
from autotransform.common.runner import Runner
from autotransform.filter.extension import ExtensionFilter
from autotransform.input.directory import DirectoryInput
from autotransform.repo.git import GitRepo
from autotransform.repo.github import GithubRepo
from autotransform.transformer.regex import RegexTransformer
from autotransform.worker.local import LocalWorker


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Runs simple regex based codemods")
    parser.add_argument(
        "-e",
        "--extensions",
        metavar="extensions",
        type=str,
        required=False,
        help="A comma separated list of extensions for files to modify",
    )
    parser.add_argument(
        "-d",
        "--directory",
        metavar="directory",
        type=str,
        required=True,
        help="The directory to search within within for files to modify",
    )
    parser.add_argument(
        "--git",
        metavar="git_repo_path",
        type=str,
        required=False,
        help="The absolute path to a git repo containing the directory",
    )
    parser.add_argument(
        "--github",
        metavar="repo_name",
        type=str,
        required=False,
        help="The full name of the github repo that a pull request should be submitted against",
    )
    parser.add_argument("pattern", metavar="pattern", type=str, help="The pattern to be replaced")
    parser.add_argument(
        "replacement", metavar="replacement", type=str, help="What you wish to replace with"
    )
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
        extensions = ["." + extension for extension in extensions]
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
    package = AutoTransformPackage(inp, batcher, transformer, filters=filters, repo=repo)
    runner = Runner(package, LocalWorker)
    start_time = time.time()
    runner.start()
    timeout = 30
    while not runner.is_finished() and time.time() <= start_time + timeout:
        time.sleep(1)
    runner.kill()


if __name__ == "__main__":
    main()
