import logging
import sys

import gsy_matching_engine_sdk

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(console_handler)

logger.warning(
    "The myco_api_client package name will be deprecated soon. Please use gsy_matching_engine_sdk instead.")

__all__ = ["gsy_matching_engine_sdk"]

sys.modules[__name__] = sys.modules["gsy_matching_engine_sdk"]
