"""
Update Logger

Description: Convenient and beautiful logging of your data.
License: MIT
"""


__version__ = "1.0.0"
__author__ = "Darkangel"
__license__ = "MIT"


from .upd_logger import Logger

__all__ = ["Logger"]


import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())