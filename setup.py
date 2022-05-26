# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Sets up the build for AutoTransform."""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AutoTransform",
    version="0.2.2a1",
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
    package_dir={"": "."},
    packages=setuptools.find_packages(),
    install_requires=[
        "GitPython>=3.1.27",
        "ghapi>=0.1.20",
        "typing-extensions>=4.2.0",
        "colorama>=0.4.4",
        "pytz>=2022.1",
        "configparser>=5.2.0",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "autotransform = autotransform.scripts.main:main",
        ]
    },
    package_data={
        "": [
            "examples/sample_config.ini",
            "examples/schedule.json",
            "examples/manage.json",
            "examples/requirements.txt",
            "examples/schemas/black_format.json",
            "examples/workflows/autotransform_manage.yml",
            "examples/workflows/autotransform_run.yml",
            "examples/workflows/autotransform_schedule.yml",
            "examples/workflows/autotransform_update.yml",
        ],
    },
)
