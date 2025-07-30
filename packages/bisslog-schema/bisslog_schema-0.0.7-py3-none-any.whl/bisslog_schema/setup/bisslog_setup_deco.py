"""
Module for registering Bisslog setup and runtime configuration decorators.

This module provides two decorators:
- `@bisslog_setup`: Used to define a global setup function for initializing application state.
- `@bisslog_runtime_config`: Used to register configuration functions specific to one
 or more runtimes.

These decorators store the configuration in a shared `BisslogSetupRegistry`, allowing the
framework to introspect or execute appropriate functions depending on the runtime context.
"""

from typing import Callable
from .bisslog_setup_registry import BisslogSetupRegistry

setup_registry = BisslogSetupRegistry()

def bisslog_setup(*, enabled: bool = True):
    """
    Decorator to register a global Bisslog setup function.

    This setup function is executed once during application initialization,
    before any runtime-specific configurations are applied. Only one setup
    function can be registered; multiple definitions will raise a RuntimeError.

    Parameters
    ----------
    enabled : bool, optional
        Whether this setup should be registered. Defaults to True.

    Returns
    -------
    Callable
        The decorated function unchanged.
    """
    def decorator(func: Callable):
        return setup_registry.register_setup(func, enabled=enabled)
    return decorator

def bisslog_runtime_config(*runtimes: str, enabled: bool = True):
    """
    Decorator to register runtime-specific configuration functions.

    The function will be invoked only when the runtime matches one of the specified values.
    Wildcard notation is supported (e.g., "*-flask" means all runtimes except 'flask').

    Parameters
    ----------
    *runtimes : str
        One or more runtime identifiers (e.g., "cli", "flask", "*-kafka").
    enabled : bool, optional
        Whether this configuration should be registered. Defaults to True.

    Returns
    -------
    Callable
        The decorated function unchanged.

    Raises
    ------
    ValueError
        If no runtimes are specified, or if unknown runtime identifiers are used.
    """
    def decorator(func: Callable):
        return setup_registry.register_runtime_config(func, list(runtimes), enabled=enabled)
    return decorator
