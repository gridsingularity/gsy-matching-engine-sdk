__version__ = '0.1.0'

from abc import ABC, abstractmethod


class MycoMatcherClientInterface(ABC):
    """
    Interface for Myco Matching API clients, that support different communication protocols.
    This interface defines the common user functionality that these clients should
    support.
    """
    def request_offers_bids(self):
        """
        This method contains the code that queries the open offers/bids in the simulation
        :return:
        """

    def on_offers_bids_response(self, data):
        """
        This method can be overridden to perform specific orders after bids/offers response is returned
        :param data: Contains data of the open offers/ bids in the format:
        { "market_offers_bids_list_mapping": {market_uuid: {"offers": [...], "bids": [...]}}}
        :return:
        """

    def on_tick(self, data):
        """

        :param data:
        :return:
        """

    def on_market_cycle(self, data):
        """

        :param data:
        :return:
        """

    def on_finish(self, data):
        """

        :param data:
        :return:
        """

    def on_event_or_response(self, data):
        """

        :param data:
        :return:
        """

    def on_matched_recommendations_response(self, data):
        """
        This method will be called when the sent recommendations' response is returned
        :param data:
        :return:
        """

    def submit_matches(self, recommended_matches):
        """
        This method is meant to post the recommended_matches to d3a
        :param recommended_matches: list of recommended trades List[BidOfferMatch.serializable_dict()
        :return:
        """
