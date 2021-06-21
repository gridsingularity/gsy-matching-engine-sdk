from abc import ABC, abstractmethod


class MycoMatcherClientInterface(ABC):
    """Interface for Myco Matching API clients, that support different communication protocols.

    This interface defines the common user functionality that these clients should
    support.
    """
    @abstractmethod
    def request_offers_bids(self):
        """This method contains the code that queries the open offers/bids in the simulation.

        Returns: None
        """

    @abstractmethod
    def on_offers_bids_response(self, data):
        """This method can be overridden to perform specific orders after bids/offers response is returned.

        Args:
            data: Contains data of the open offers/ bids in the format:
        { "market_offers_bids_list_mapping": {market_uuid: {"offers": [...], "bids": [...]}}}

        Returns: None
        """

    @abstractmethod
    def on_matched_recommendations_response(self, data):
        """This method will be called when the sent recommendations' response is returned.

        Args:
            data:

        Returns: None
        """

    @abstractmethod
    def submit_matches(self, recommended_matches):
        """This method is meant to post the recommended_matches to d3a.

        Args:
            recommended_matches: list of recommended trades List[BidOfferMatch.serializable_dict()

        Returns: None
        """

    def on_tick(self, data):
        pass

    def on_market_cycle(self, data):
        pass

    def on_finish(self, data):
        pass

    def on_event_or_response(self, data):
        pass
