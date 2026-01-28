"""
Root pytest configuration file.

Delegates all fixture and hook configuration to core/conftest.py.
This allows the framework code to be colocated with its configuration.
"""

pytest_plugins = ["core.conftest"]

