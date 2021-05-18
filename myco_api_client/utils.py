import os
from typing import List, Dict

from myco_api_client.constants import DEFAULT_DOMAIN_NAME, DEFAULT_WEBSOCKET_DOMAIN, \
    MYCO_CLIENT_SIMULATION_ID


def sort_list_of_dicts_by_attribute(input_list: List[Dict],
                                    attribute: str,
                                    reverse_order=False):
    """
    Sorts a list of dicts by a given attribute
    If reverse_order is True, the returned list will be sorted in descending order

    :return: List[Dict]
    """
    return sorted(input_list,
                  key=lambda bid_offer: bid_offer.get(attribute),
                  reverse=reverse_order)


def domain_name_from_env():
    return os.environ.get("MYKO_CLIENT_DOMAIN_NAME", DEFAULT_DOMAIN_NAME)


def websocket_domain_name_from_env():
    return os.environ.get("MYKO_CLIENT_WEBSOCKET_DOMAIN_NAME", DEFAULT_WEBSOCKET_DOMAIN)


def simulation_id_from_env():
    return os.environ.get("MYKO_CLIENT_SIMULATION_ID", MYCO_CLIENT_SIMULATION_ID)
