# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that the Repo's factory is correctly setup."""

from typing import Any, Dict, List

from autotransform.repo.base import FACTORY, RepoName


def test_all_enum_values_present():
    """Ensures that all values from the enum are present in the factory map,
    and only enum values are present."""

    components = FACTORY.get_components()
    missing_values = [repo_name for repo_name in RepoName if repo_name not in components]
    assert not missing_values, f"Names missing from factory: {', '.join(missing_values)}"

    extra_values = [repo_name for repo_name in components if repo_name not in RepoName]
    assert not extra_values, f"Extra names in factory: {', '.join(extra_values)}"


def test_fetching_components():
    """Ensures that all components can be fetched correctly."""

    for component_name in FACTORY.get_components():
        component_class = FACTORY.get_class(component_name)
        assert (
            component_class.name == component_name
        ), f"Component {component_name} has wrong name {component_class.name}"

    for component_name in FACTORY.get_custom_components(strict=True):
        component_class = FACTORY.get_class(component_name)
        assert (
            f"custom/{component_class.name}" == component_name
        ), f"Component {component_name} has wrong name {component_class.name}"


def test_encoding_and_decoding() -> None:
    """Tests the encoding and decoding of components."""

    test_components: Dict[RepoName, List[Dict[str, Any]]] = {
        RepoName.GIT: [
            {"base_branch": "master"},
        ],
        RepoName.GITHUB: [
            {"base_branch": "master", "full_github_name": "nathro/AutoTransform"},
            {
                "base_branch": "master",
                "full_github_name": "nathro/AutoTransform",
                "labels": ["foo"],
            },
            {
                "base_branch": "master",
                "full_github_name": "nathro/AutoTransform",
                "hide_automation_info": True,
            },
            {
                "base_branch": "master",
                "full_github_name": "nathro/AutoTransform",
                "hide_autotransform_docs": True,
            },
            {
                "base_branch": "master",
                "full_github_name": "nathro/AutoTransform",
                "labels": ["foo"],
                "hide_automation_info": True,
            },
            {
                "base_branch": "master",
                "full_github_name": "nathro/AutoTransform",
                "labels": ["foo"],
                "hide_autotransform_docs": True,
            },
            {
                "base_branch": "master",
                "full_github_name": "nathro/AutoTransform",
                "hide_automation_info": True,
                "hide_autotransform_docs": True,
            },
            {
                "base_branch": "master",
                "full_github_name": "nathro/AutoTransform",
                "labels": ["foo"],
                "hide_automation_info": True,
                "hide_autotransform_docs": True,
            },
            {
                "base_branch": "master",
                "full_github_name": "nathro/AutoTransform",
                "reviewers": ["foo"],
                "hide_automation_info": True,
                "hide_autotransform_docs": True,
            },
            {
                "base_branch": "master",
                "full_github_name": "nathro/AutoTransform",
                "team_reviewers": ["foo"],
                "hide_automation_info": True,
                "hide_autotransform_docs": True,
            },
            {
                "base_branch": "master",
                "full_github_name": "nathro/AutoTransform",
                "reviewers": ["foo"],
            },
            {
                "base_branch": "master",
                "full_github_name": "nathro/AutoTransform",
                "team_reviewers": ["foo"],
            },
            {
                "base_branch": "master",
                "full_github_name": "nathro/AutoTransform",
                "reviewers": ["foo"],
                "team_reviewers": ["bar"],
            },
        ],
    }

    for name in RepoName:
        assert name in test_components, f"No test components for Repo {name}"

    for name, components in test_components.items():
        for component in components:
            component_dict = {"name": name, **component}
            component_instance = FACTORY.get_instance(component_dict)
            assert (
                component_instance.name == name
            ), f"Testing Repo of name {component_instance.name} for name {name}"
            assert component_dict == component_instance.bundle()
