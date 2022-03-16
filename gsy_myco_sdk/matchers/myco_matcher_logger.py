"""Module for the logger used by Myco matcher classes."""

import logging
from typing import Dict

from gsy_framework.constants_limits import DEFAULT_PRECISION
from tabulate import tabulate


class MycoMatcherLogger:
    """Custom logger used by instances of Myco matchers."""

    @staticmethod
    def log_recommendations_response(markets: Dict, data: Dict) -> None:
        """Log the response data of recommendations sent to the clearing mechanism.

        Args:
            markets: a dictionary with the following structure:
                {
                    "<market-id>": {
                        "<time-slot-1>": {"market_type_name": "<market-type-name>"}
                        "<time-slot-2>": {"market_type_name": "<market-type-name>"}
                    }
                }
        """
        recommendations = data["recommendations"]
        if not recommendations:
            return
        logging.info("Length of recommendations: %s", len(recommendations))
        recommendations_table = []
        recommendations_table_headers = [
            "#",
            "Market Type Name",
            "Buyer", "Seller",
            "Bid kWh", "Offer kWh", "Status", "Message"]

        # Orders can get forwarded to higher/lower markets
        # In order not to log all propagations of the same orders, a workaround
        # would be to cache the already logged orders' attributes that do not change when forwarded
        orders_cache = set()
        index = 1

        for recommendation in recommendations:
            cached_market_info = markets.get(recommendation["market_id"])
            time_slot = recommendation["time_slot"]
            market_type_name = cached_market_info[time_slot][
                "market_type_name"] if cached_market_info else "Unknown"

            bid = recommendation["bid"]
            offer = recommendation["offer"]
            offer_data = (f"{round(offer['energy'], DEFAULT_PRECISION)}-"
                          f"{round(offer['original_price'], DEFAULT_PRECISION)}-"
                          f"{offer['seller_origin_id']}-{offer['time_slot']}")
            bid_data = (f"{round(bid['energy'], DEFAULT_PRECISION)}-"
                        f"{round(bid['original_price'], DEFAULT_PRECISION)}-"
                        f"{bid['buyer_origin_id']}-{bid['time_slot']}")
            if offer_data not in orders_cache or bid_data not in orders_cache:
                recommendations_table.append([
                    index,
                    market_type_name,
                    bid.get("buyer_origin"),
                    offer.get("seller_origin"),
                    bid.get("energy"),
                    offer.get("energy"),
                    recommendation["status"],
                    recommendation.get("message")])
                index += 1
                orders_cache.add(offer_data)
                orders_cache.add(bid_data)
        logging.info("\n%s", tabulate(recommendations_table, recommendations_table_headers,
                                      tablefmt="fancy_grid"))
