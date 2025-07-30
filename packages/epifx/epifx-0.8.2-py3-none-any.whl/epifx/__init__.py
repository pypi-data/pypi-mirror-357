"""Epidemic forecasts using disease surveillance data."""

import logging

from . import model
from . import det
from . import stoch
from . import obs
from . import summary
from . import select


# Export classes from this module.
Model = model.Model

# Prevent an error message if the application does not configure logging.
log = logging.getLogger(__name__).addHandler(logging.NullHandler())

# Define the items that "from epifx import *" should import.
__all__ = ['model', 'det', 'stoch', 'obs', 'summary', 'select', 'Model']
