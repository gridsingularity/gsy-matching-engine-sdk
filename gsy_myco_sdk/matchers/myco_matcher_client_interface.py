from abc import ABC, abstractmethod
from typing import Dict, List

from gsy_framework.data_classes import BidOfferMatch


class MycoMatcherClientInterface(ABC):
    """Interface for Myco Matching API clients, that support different communication protocols.

    This interface defines the common user functionality that these clients should
    support.
    """

    _markets_cache: Dict[str, Dict]  # Cached information about markets and time slots

    @abstractmethod
    def request_offers_bids(self, filters: Dict):
        """This method contains the code that queries the open offers/bids in the simulation.

        Returns: None
        """

    @abstractmethod
    def on_offers_bids_response(self, data: Dict):
        """Perform specific actions after bids/offers response is returned.

        Args:
            data: Contains data of the open offers/ bids in the format:
        { "bids_offers": {market_uuid: {"offers": [...], "bids": [...]}}}

        Returns: None
        """

    @abstractmethod
    def on_matched_recommendations_response(self, data: Dict):
        """This method will be called when the sent recommendations' response is returned.

        Args:
            data: Response returned after matching recommendations call on exchange

        Returns: None
        """

    @abstractmethod
    def submit_matches(self, recommended_matches: List[BidOfferMatch.serializable_dict]):
        """This method is meant to post the recommended_matches to exchange.

        Args:
            recommended_matches: list of recommended trades List[BidOfferMatch.serializable_dict()

        Returns: None
        """

    def on_tick(self, data: Dict):
        """Tick event handler."""

    def on_market_cycle(self, data: Dict):
        """Market cycle event handler."""

    def on_finish(self, data: Dict):
        """Finish event handler."""

    def on_event_or_response(self, data: Dict):
        """Extra handler for all events/responses callbacks."""

    def on_area_map_response(self, data: Dict):
        """Updated Area UUID Name map event handler."""

    def _cache_markets_information(self, data: Dict[str, Dict]):
        """Store information about markets in a cache, to be reused in later events.

        Structure example:
            {
                "<market-id-1>": {"type_name": "<market-type-name>", "time_slots": [...]}
                "<market-id-2>": {"type_name": "<market-type-name>", "time_slots": [...]}
            }
        """
        markets_info = data["markets_info"]
        # Convert the list of time slots of each market into a set for improved performance
        for market_id, market_info in markets_info.items():
            time_slots = market_info["time_slots"]
            markets_info[market_id]["time_slots"] = set(time_slots)

        self._markets_cache = markets_info  # Replace existing cache
