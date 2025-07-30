import warnings
import logging

from classicist import hybridmethod

logger = logging.getLogger(__name__)

warnings.warn(
    "The 'hybridmethod' library has been deprecated and superseded by the 'classicist' library. Please update any dependency definitions and import statements to reference the new 'classicist' library instead from which the `hybridmethod` decorator can be imported.",
    DeprecationWarning,
    stacklevel=2,
)
