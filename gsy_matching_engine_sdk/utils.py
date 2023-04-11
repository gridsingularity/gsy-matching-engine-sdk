import os

from gsy_matching_engine_sdk.constants import (
    DEFAULT_DOMAIN_NAME, DEFAULT_WEBSOCKET_DOMAIN, MATCHING_ENGINE_SIMULATION_ID)


def domain_name_from_env():
    """Retrieve the Matching Engine domain name from the environment variables."""
    return os.environ.get("MATCHING_ENGINE_DOMAIN_NAME", DEFAULT_DOMAIN_NAME)


def websocket_domain_name_from_env():
    """Retrieve the Matching Engine websocket's domain name from the environment variables."""
    return os.environ.get("MATCHING_ENGINE_WEBSOCKET_DOMAIN_NAME", DEFAULT_WEBSOCKET_DOMAIN)


def simulation_id_from_env():
    """
    Retrieve the ID of the simulation that the Matching Engine
    should target from the env variables.
    """
    return os.environ.get("MATCHING_ENGINE_SIMULATION_ID", MATCHING_ENGINE_SIMULATION_ID)
