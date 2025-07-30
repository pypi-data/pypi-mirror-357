"""
Version

Description: Makes it easier to work with versions for your projects.
License: MIT
"""


__version__ = "1.0.0"
__author__ = "Darkangel"
__license__ = "MIT"


from .version import Version

__all__ = ["Version"]

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())