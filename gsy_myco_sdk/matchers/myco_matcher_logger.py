"""Module for the logger used by Myco matcher classes."""

import logging
from typing import Dict, Optional

from gsy_framework.constants_limits import DEFAULT_PRECISION
from tabulate import tabulate


LOGGER = logging.getLogger(__name__)


class MycoMatcherLogger:
    """Custom logger used by instances of Myco matchers."""

    @staticmethod
    def _get_market_type_name_by_time_slot(
            markets_info: Dict[str, Dict], time_slot: str) -> Optional[str]:
        """Iterate through all market objects to find the one that contains the current time slot.

        NOTE: Future market objects contain multiple time slots.
        """
        for market_info in markets_info.values():
            if time_slot in market_info["time_slots"]:
                return market_info["type_name"]

        return None

    @classmethod
    def log_recommendations_response(cls, markets_info: Dict, data: Dict) -> None:
        """Log the response data of recommendations sent to the clearing mechanism.

        Args:
            markets_info: a dictionary with the following structure:
                {
                    "<market-id-1>": {"type_name": "<market-type-name>", "time_slots": {...}}
                    "<market-id-2>": {"type_name": "<market-type-name>", "time_slots": {...}}
                }
        """
        recommendations = data["recommendations"]
        if not recommendations:
            return
        LOGGER.info("Length of recommendations: %s", len(recommendations))
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
            time_slot = recommendation["time_slot"]
            market_type_name = cls._get_market_type_name_by_time_slot(markets_info, time_slot)
            bid = recommendation["bid"]
            offer = recommendation["offer"]
            offer_data = (f"{round(offer['energy'], DEFAULT_PRECISION)}-"
                          f"{round(offer['original_price'], DEFAULT_PRECISION)}-"
                          f"{offer['seller']['origin_uuid']}-{offer['time_slot']}")
            bid_data = (f"{round(bid['energy'], DEFAULT_PRECISION)}-"
                        f"{round(bid['original_price'], DEFAULT_PRECISION)}-"
                        f"{bid['buyer']['origin_uuid']}-{bid['time_slot']}")
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
        LOGGER.info(
            "\n%s", tabulate(
                recommendations_table, recommendations_table_headers, tablefmt="fancy_grid"))
