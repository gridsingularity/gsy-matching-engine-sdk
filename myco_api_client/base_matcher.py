from concurrent.futures.thread import ThreadPoolExecutor
from typing import List, Dict

from d3a_interface.client_connections.utils import (
    RestCommunicationMixin, retrieve_jwt_key_from_server)
from d3a_interface.client_connections.websocket_connection import WebsocketThread
from d3a_interface.constants_limits import FLOATING_POINT_TOLERANCE

from myco_api_client import MycoMatcherClientInterface
from myco_api_client.constants import MAX_WORKER_THREADS
from myco_api_client.dataclasses import BidOfferMatch
from myco_api_client.utils import (
    sort_list_of_dicts_by_attribute, simulation_id_from_env,
    domain_name_from_env, websocket_domain_name_from_env)
from myco_api_client.websocket_device import WebsocketMessageReceiver


class BaseMatcher(MycoMatcherClientInterface, RestCommunicationMixin):
    def __init__(self, simulation_id=None, domain_name=None, websocket_domain_name=None,
                 auto_connect=True):
        self.simulation_id = simulation_id if simulation_id else simulation_id_from_env()
        self.domain_name = domain_name if domain_name else domain_name_from_env()
        self.websocket_domain_name = websocket_domain_name \
            if websocket_domain_name else websocket_domain_name_from_env()
        self.dispatcher = self.websocket_thread = self.callback_thread = None
        self.jwt_token = retrieve_jwt_key_from_server(self.domain_name)
        self._create_jwt_refresh_timer(self.domain_name)
        if auto_connect:
            self.start_websocket_connection()

    def start_websocket_connection(self):
        self.dispatcher = WebsocketMessageReceiver(self)
        self.websocket_thread = WebsocketThread(self.simulation_id,
                                                self.websocket_domain_name, self.domain_name,
                                                self.dispatcher)
        self.websocket_thread.start()
        self.callback_thread = ThreadPoolExecutor(max_workers=MAX_WORKER_THREADS)

    def calculate_match_recommendations(self, market_offers_bids_list_mapping):
        recommendations = self._perform_pay_as_bid_match(market_offers_bids_list_mapping)
        return recommendations

    @staticmethod
    def _perform_pay_as_bid_match(market_offers_bids_list_mapping):
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

    def submit_matches(self, recommended_matches):
        self._post_request("post_recommendations", recommended_matches)

    def request_orders(self, filters=None):
        self._get_request("get_offers_bids", {"filters": filters})

    def on_bids_offers_response(self, message):
        recommendations = self.calculate_match_recommendations(
            message.get("market_offers_bids_list_mapping"))
        self.submit_matches(recommendations)
