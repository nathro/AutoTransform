"""Sets up some configuration for PyTest."""

from autotransform.change.base import TestState

# Prevent pytest from trying to collect TestState as tests:
TestState.__test__ = False  # type: ignore
