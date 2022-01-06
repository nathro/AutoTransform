import argparse
from typing import List

from batcher.single import SingleBatcher
from common.package import AutoTransformPackage
from filter.extension import ExtensionFilter, Extensions
from input.directory import DirectoryInput
from repo.git import GitRepo
from transformer.regex import RegexTransformer

def parse_arguments():
    parser = argparse.ArgumentParser(description="Runs simple regex based codemods")
    parser.add_argument("-e", "--extensions", metavar="extensions", type=str, required=False, help="A comma separated list of extensions for files to modify")
    parser.add_argument("-d", "--directory", metavar="directory", type=str, required=True, help="The directory to search within within for files to modify")
    parser.add_argument("pattern", metavar="pattern", type=str, help="The pattern to be replaced")
    parser.add_argument("replacement", metavar="replacement", type=str, help="What you wish to replace with")
    return parser.parse_args()

def main():
    args = parse_arguments()
    input = DirectoryInput({"path": args.directory})
    transformer = RegexTransformer({"pattern": args.pattern, "replacement": args.replacement})
    batcher = SingleBatcher({"metadata": {"title": "Just a test", "summary": "This is just a test", "tests": "This?"}})
    repo = GitRepo({"path": "C:/repos/autotransform"})
    filters = []
    extensions = args.extensions
    if isinstance(extensions, str):
        extensions = extensions.split(",")
        extensions = ["." + extension for extension in extensions]
        for extension in extensions:
            assert Extensions.has_value(extension)
        filters.append(ExtensionFilter({"extensions": extensions}))
    
    package = AutoTransformPackage(input, batcher, transformer, filters=filters, repo=repo)
    package.run()

if __name__ == "__main__":
    main()