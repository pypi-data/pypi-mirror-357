"""
ApiChainer: A declarative Python library for building chained HTTP request workflows.
"""

# Version
__version__ = "0.1.0"

# Expose the main classes and exceptions at the top level of the package
from .main import ApiChain, AsyncApiChain, ChainError, PlaceholderError, PollingTimeoutError, RequestError

__all__ = [
    "ApiChain",
    "AsyncApiChain",
    "ChainError",
    "RequestError",
    "PlaceholderError",
    "PollingTimeoutError",
    "__version__",
]
