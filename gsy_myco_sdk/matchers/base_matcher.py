import logging
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Dict

from gsy_framework.client_connections.utils import (
    RestCommunicationMixin, retrieve_jwt_key_from_server)
from gsy_framework.client_connections.websocket_connection import WebsocketThread

from gsy_myco_sdk.matchers.myco_matcher_client_interface import MycoMatcherClientInterface
from gsy_myco_sdk.constants import MAX_WORKER_THREADS
from gsy_myco_sdk.utils import (
    simulation_id_from_env, domain_name_from_env, websocket_domain_name_from_env,
    )
from gsy_myco_sdk.websocket_device import WebsocketMessageReceiver


class BaseMatcher(MycoMatcherClientInterface, RestCommunicationMixin):
    def __init__(self, simulation_id=None, domain_name=None, websocket_domain_name=None,
                 auto_connect=True):
        self.simulation_id = simulation_id if simulation_id else simulation_id_from_env()
        self.domain_name = domain_name if domain_name else domain_name_from_env()
        self.websocket_domain_name = (
            websocket_domain_name if websocket_domain_name else websocket_domain_name_from_env())
        self.dispatcher = self.websocket_thread = self.callback_thread = None
        self.jwt_token = retrieve_jwt_key_from_server(self.domain_name)
        self._create_jwt_refresh_timer(self.domain_name)
        self.url_prefix = f"{self.domain_name}/external-connection/api/{self.simulation_id}"
        if auto_connect:
            self.start_websocket_connection()

    def start_websocket_connection(self):
        self.dispatcher = WebsocketMessageReceiver(self)
        websocket_uri = f"{self.websocket_domain_name}/{self.simulation_id}/myco/"
        self.websocket_thread = WebsocketThread(websocket_uri, self.domain_name,
                                                self.dispatcher)
        self.websocket_thread.start()
        self.callback_thread = ThreadPoolExecutor(max_workers=MAX_WORKER_THREADS)
        logging.info("Connection to gsy-e has been established (simulation_id: %s).",
                     self.simulation_id)

    def submit_matches(self, recommended_matches):
        if recommended_matches:
            logging.debug("Sending recommendations %s.", recommended_matches)
            data = {"recommended_matches": recommended_matches}
            self._post_request(f"{self.url_prefix}/recommendations", data)

    def request_offers_bids(self, filters: Dict = None):
        self._get_request(f"{self.url_prefix}/offers-bids", {"filters": filters})

    def _on_offers_bids_response(self, data):
        self.on_offers_bids_response(data)

    def on_offers_bids_response(self, data):
        recommendations = []
        self.submit_matches(recommendations)

    def _on_match(self, data):
        self.on_matched_recommendations_response(data)

    def on_matched_recommendations_response(self, data):
        pass

    def _on_tick(self, data):
        self.on_tick(data)

    def _on_market_cycle(self, data):
        self.on_market_cycle(data)

    def _on_finish(self, data):
        self.on_finish(data)
