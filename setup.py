# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AutoTransform",
    version="0.0.9",
    author="Nathan Rockenbach",
    author_email="nathro.software@gmail.com",
    description="A component based tool for designing automated code modification",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nathro/AutoTransform",
    project_urls={
        "Bug Tracker": "https://github.com/nathro/AutoTransform/issues",
        "Source": "https://github.com/nathro/AutoTransform/",
        "Say Thanks!": "https://saythanks.io/to/nathro.software",
        "Support": "https://www.paypal.com/paypalme/nathrosoftware",
        "Stream": "https://www.twitch.tv/AllSublime",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="codemod, automation, code change",
    package_dir={"": "."},
    packages=setuptools.find_packages(),
    install_requires=["GitPython", "PyGithub"],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "regexmod = autotransform.regexmod:main",
            "atmanager = autotransform.manager:main",
        ]
    },
    package_data={"": ["data/sample_config.ini", "data/packages/sample_package.json"]},
)
