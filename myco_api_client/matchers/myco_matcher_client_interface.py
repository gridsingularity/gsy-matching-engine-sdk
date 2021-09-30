from abc import ABC, abstractmethod
from typing import Dict, List

from d3a_interface.data_classes import BidOfferMatch


class MycoMatcherClientInterface(ABC):
    """Interface for Myco Matching API clients, that support different communication protocols.

    This interface defines the common user functionality that these clients should
    support.
    """
    @abstractmethod
    def request_offers_bids(self, filters: Dict):
        """This method contains the code that queries the open offers/bids in the simulation.

        Returns: None
        """

    @abstractmethod
    def on_offers_bids_response(self, data: Dict):
        """This method can be overridden to perform specific actions after bids/offers response is returned.

        Args:
            data: Contains data of the open offers/ bids in the format:
        { "bids_offers": {market_uuid: {"offers": [...], "bids": [...]}}}

        Returns: None
        """

    @abstractmethod
    def on_matched_recommendations_response(self, data: Dict):
        """This method will be called when the sent recommendations' response is returned.

        Args:
            data: Response returned after matching recommendations call on d3a

        Returns: None
        """

    @abstractmethod
    def submit_matches(self, recommended_matches: List[BidOfferMatch.serializable_dict]):
        """This method is meant to post the recommended_matches to d3a.

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
