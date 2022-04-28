import os

from gsy_myco_sdk.constants import (
    DEFAULT_DOMAIN_NAME, DEFAULT_WEBSOCKET_DOMAIN, MYCO_CLIENT_SIMULATION_ID)


def domain_name_from_env():
    """Retrieve the Myco domain name from the environment variables."""
    return os.environ.get("MYCO_CLIENT_DOMAIN_NAME", DEFAULT_DOMAIN_NAME)


def websocket_domain_name_from_env():
    """Retrieve the Myco websocket's domain name from the environment variables."""
    return os.environ.get("MYCO_CLIENT_WEBSOCKET_DOMAIN_NAME", DEFAULT_WEBSOCKET_DOMAIN)


def simulation_id_from_env():
    """Retrieve the ID of the simulation that the Myco should target from the env variables."""
    return os.environ.get("MYCO_CLIENT_SIMULATION_ID", MYCO_CLIENT_SIMULATION_ID)
