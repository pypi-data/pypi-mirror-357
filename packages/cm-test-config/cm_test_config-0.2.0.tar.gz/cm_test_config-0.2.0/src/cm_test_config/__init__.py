# Version of the package
__version__ = "0.1.0"

# Import key functions/classes to make them available at package level
from .example import greet

# List of what gets imported with 'from cm_test_config import *'
__all__ = ['greet']