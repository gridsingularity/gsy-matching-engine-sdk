import os
from typing import List, Dict

from d3a_interface.constants_limits import FLOATING_POINT_TOLERANCE

from myco_api_client.constants import DEFAULT_DOMAIN_NAME, DEFAULT_WEBSOCKET_DOMAIN, \
    MYCO_CLIENT_SIMULATION_ID
from myco_api_client.dataclasses import BidOfferMatch


def sort_list_of_dicts_by_attribute(input_list: List[Dict],
                                    attribute: str,
                                    reverse_order=False):
    """Sorts a list of dicts by a given attribute.

    Args:
        input_list: List[Dict]
        attribute: attribute to sort against
        reverse_order: if True, the returned list will be sorted in descending order

    Returns: List[Dict]

    """

    return sorted(input_list,
                  key=lambda bid_offer: bid_offer.get(attribute),
                  reverse=reverse_order)


def domain_name_from_env():
    return os.environ.get("MYCO_CLIENT_DOMAIN_NAME", DEFAULT_DOMAIN_NAME)


def websocket_domain_name_from_env():
    return os.environ.get("MYCO_CLIENT_WEBSOCKET_DOMAIN_NAME", DEFAULT_WEBSOCKET_DOMAIN)


def simulation_id_from_env():
    return os.environ.get("MYCO_CLIENT_SIMULATION_ID", MYCO_CLIENT_SIMULATION_ID)


def perform_pay_as_bid_match(market_offers_bids_list_mapping):
    """Performs pay as bid matching algorithm.

    Args:
        market_offers_bids_list_mapping:
        { "market_offers_bids_list_mapping": {market_uuid: {"offers": [...], "bids": [...]}}}

    Returns: List[BidOfferMatch.serializable_dict()]
    TODO: Export this function to d3a-interface
    """
    bid_offer_pairs = []
    for market_id, data in market_offers_bids_list_mapping.items():
        bids = data.get("bids")
        offers = data.get("offers")
        # Sorted bids in descending order
        sorted_bids = sort_list_of_dicts_by_attribute(bids, "energy_rate", True)
        # Sorted offers in descending order
        sorted_offers = sort_list_of_dicts_by_attribute(offers, "energy_rate", True)
        already_selected_bids = set()
        for offer in sorted_offers:
            for bid in sorted_bids:
                if bid.get("id") in already_selected_bids or\
                        offer.get("seller") == bid.get("buyer"):
                    continue
                if (offer.get("energy_rate") - bid.get("energy_rate")) <= FLOATING_POINT_TOLERANCE:
                    already_selected_bids.add(bid.get("id"))
                    selected_energy = min(bid.get("energy"), offer.get("energy"))
                    bid_offer_pairs.append(BidOfferMatch(market_id=market_id,
                                                         bid=bid, offer=offer,
                                                         selected_energy=selected_energy,
                                                         trade_rate=bid.get("energy_rate"))
                                           .serializable_dict())
                    break
    return bid_offer_pairs
