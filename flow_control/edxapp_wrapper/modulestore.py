"""
Modulestore module generalized definitions.
"""

from importlib import import_module
from django.conf import settings


def get_modulestore_module_function(*args, **kwargs):
    """Get the active modulestore instance."""

    backend_function = settings.FLOW_CONTROL_MODULESTORE_MODULE_BACKEND
    backend = import_module(backend_function)

    return backend.get_modulestore(*args, **kwargs)


modulestore_module = get_modulestore_module_function
