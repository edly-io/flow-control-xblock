"""
Modulestore definitions for Open edX Sumac release.
"""
# pylint: disable=import-error
from xmodule.modulestore.django import modulestore


def get_modulestore():
    """
    Get the active modulestore instance.

    Returns:
        MixedModuleStore: the active modulestore instance.
    """
    return modulestore()
