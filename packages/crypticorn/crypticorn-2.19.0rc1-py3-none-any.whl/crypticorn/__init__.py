"""
.. include:: ../README.md

## Versioning
We adhere to [Semantic Versioning](https://semver.org/).
You can find the full Changelog [below](#changelog).
"""

import warnings
import logging
from crypticorn.common.logging import configure_logging

warnings.filterwarnings("default", "", DeprecationWarning)
configure_logging()
logging.captureWarnings(True)
# TODO: remove folder in next major release

from crypticorn.client import AsyncClient, SyncClient, ApiClient

__all__ = ["AsyncClient", "SyncClient", "ApiClient"]
