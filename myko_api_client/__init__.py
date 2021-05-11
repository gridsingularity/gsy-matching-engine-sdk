__version__ = '0.1.0'

from abc import ABC, abstractmethod


class MykoMatcherClientInterface(ABC):
    """
    Interface for Myko Matching API clients, that support different communication protocols.
    This interface defines the common user functionality that these clients should
    support.
    """

    @abstractmethod
    def calculate_match_recommendation(self, market_offers_bids_list_mapping):
        """
        This method will calculate the recommended bids/offers matches
        :param market_offers_bids_list_mapping: mapping as {"market_id": {"bids": [], "offers": []}}
        :return: list of BidOfferMatch objects
        """
    def on_bids_offers_response(self, message):
        """
        This method can be overridden to perform specific orders after bids/offers response is returned
        :param message:
        :return:
        """
