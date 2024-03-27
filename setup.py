# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Sets up the build for AutoTransform."""

import os
from typing import List, Tuple

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def generate_datafiles() -> List[Tuple[str, List[str]]]:
    """Generates the data files for set-up

    Returns:
        List[Tuple[str, List[str]]]: The datafiles for setup.
    """

    data_files = [
        (
            "autotransform-docs",
            [
                "BEST_PRACTICES.md",
                "COMPONENTS.md",
                "CONTRIBUTING.md",
                "CUSTOM_DEPLOYMENT.md",
                "MANAGE_CHANGES.md",
                "README.md",
                "SCHEDULED_RUNS.md",
            ],
        )
    ]

    for path, _, files in os.walk("examples"):
        data_files.append(
            (f"autotransform-{path}", [os.path.join(path, file) for file in files])
        )

    return data_files


setuptools.setup(
    name="AutoTransform",
    version="1.1.1a14",
    author="Nathan Rockenbach",
    author_email="nathro.software@gmail.com",
    description="A component based framework for designing automated code modification",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nathro/AutoTransform",
    project_urls={
        "Source": "https://github.com/nathro/AutoTransform/",
        "Bug Tracker": "https://github.com/nathro/AutoTransform/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="codemod, automation, code change, codeshift, transformation, maintain",
    package_dir={"": "src/python"},
    packages=setuptools.find_packages("src/python"),
    install_requires=[
        "GitPython>=3.1.32",
        "ghapi>=1.0.3",
        "typing-extensions>=4.5.0",
        "colorama>=0.4.6",
        "pytz>=2022.7.1",
        "pydantic>=1.10.4",
        "libcst>=0.4.9",
        "requests>=2.31.0",
        "codeowners>=0.6.0",
        "openai>=0.27.8",
        "anthropic>=0.5.0",
    ],
    python_requires=">=3.9",
    data_files=generate_datafiles(),
    entry_points={
        "console_scripts": [
            "autotransform = autotransform.scripts.main:main",
            "atmigrate-1.0.1 = autotransform.scripts.migrations.p1_0_1:main",
            "atmigrate-1.0.3 = autotransform.scripts.migrations.p1_0_3:main",
            "atmigrate-1.0.5 = autotransform.scripts.migrations.p1_0_5:main",
        ],
    },
)
