import logging
import os
from typing import Dict

from gsy_framework.constants_limits import DEFAULT_PRECISION
from tabulate import tabulate

from gsy_myco_sdk.constants import DEFAULT_DOMAIN_NAME, DEFAULT_WEBSOCKET_DOMAIN, \
    MYCO_CLIENT_SIMULATION_ID


def domain_name_from_env():
    return os.environ.get("MYCO_CLIENT_DOMAIN_NAME", DEFAULT_DOMAIN_NAME)


def websocket_domain_name_from_env():
    return os.environ.get("MYCO_CLIENT_WEBSOCKET_DOMAIN_NAME", DEFAULT_WEBSOCKET_DOMAIN)


def simulation_id_from_env():
    return os.environ.get("MYCO_CLIENT_SIMULATION_ID", MYCO_CLIENT_SIMULATION_ID)


def log_recommendations_response(data: Dict) -> None:
    """Log the response data of recommendations sent to the clearing mechanism."""
    recommendations = data["recommendations"]
    if not recommendations:
        return
    logging.info("Length of recommendations: %s", len(recommendations))
    recommendations_table = []
    recommendations_table_headers = [
        "#", "Buyer", "Seller",
        "Bid kWh", "Offer kWh", "Status", "Message"]

    # Orders can get forwarded to higher/lower markets
    # In order not to log all propagations of the same orders, a workaround
    # would be to cache the already logged orders' attributes that do not change when forwarded
    orders_cache = set()
    index = 1
    for recommendation in recommendations:
        bid = recommendation["bid"]
        offer = recommendation["offer"]
        offer_data = (f"{round(offer['energy'], DEFAULT_PRECISION)}-"
                      f"{round(offer['original_price'], DEFAULT_PRECISION)}-"
                      f"{offer['seller_origin_id']}-{offer['time_slot']}")
        bid_data = (f"{round(bid['energy'], DEFAULT_PRECISION)}-"
                    f"{round(bid['original_price'], DEFAULT_PRECISION)}-"
                    f"{bid['buyer_origin_id']}-{bid['time_slot']}")
        if offer_data not in orders_cache or bid_data not in orders_cache:
            recommendations_table.append(
                [index, bid.get("buyer_origin"), offer.get("seller_origin"),
                 bid.get("energy"), offer.get("energy"), recommendation["status"],
                 recommendation.get("message")])
            index += 1
            orders_cache.add(offer_data)
            orders_cache.add(bid_data)
    logging.info("\n%s", tabulate(recommendations_table, recommendations_table_headers,
                                  tablefmt="fancy_grid"))
