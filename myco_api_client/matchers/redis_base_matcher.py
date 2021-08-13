import json
import logging
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Dict

from d3a_interface.utils import wait_until_timeout_blocking
from redis import StrictRedis

from myco_api_client.matchers.myco_matcher_client_interface import MycoMatcherClientInterface
from myco_api_client.constants import MAX_WORKER_THREADS


class RedisAPIException(Exception):
    pass


class RedisBaseMatcher(MycoMatcherClientInterface):
    def __init__(self, redis_url="redis://localhost:6379",
                 pubsub_thread=None):
        self.simulation_id = None
        self.pubsub_thread = pubsub_thread
        self.redis_db = StrictRedis.from_url(redis_url)
        self.pubsub = self.redis_db.pubsub() if pubsub_thread is None else pubsub_thread.pubsub
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKER_THREADS)
        self._get_simulation_id(is_blocking=True)
        self.redis_channels_prefix = f"external-myco/{self.simulation_id}"
        self._subscribe_to_response_channels()       

    def _set_simulation_id(self, payload):
        data = json.loads(payload["data"])
        self.simulation_id = data.get("simulation_id")
        logging.debug(f"Received Simulation ID {self.simulation_id}")

    def _check_is_set_simulation_id(self):
        return self.simulation_id is not None

    def _start_pubsub_thread(self):
        if self.pubsub_thread is None:
            self.pubsub_thread = self.pubsub.run_in_thread(daemon=True, sleep_time=0.001)

    def _get_simulation_id(self, is_blocking=True):
        self.pubsub.subscribe(**{"external-myco/simulation-id/response/":
                                 self._set_simulation_id})
        self._start_pubsub_thread()
        self.redis_db.publish("external-myco/simulation-id/", json.dumps({}))

        if is_blocking:
            try:
                wait_until_timeout_blocking(
                    lambda: self._check_is_set_simulation_id(), timeout=50
                )
            except AssertionError:
                self.simulation_id = ""  # default simulation id for cli simulations

    def _subscribe_to_response_channels(self):
        channel_subs = {
            f"{self.redis_channels_prefix}/events/":
                self._on_event_or_response,
            f"{self.redis_channels_prefix}/*/response/": self._on_event_or_response,
        }
        self.pubsub.psubscribe(**channel_subs)
        self._start_pubsub_thread()

    def submit_matches(self, recommended_matches):
        logging.debug(f"Sending recommendations {recommended_matches}")
        data = {"recommended_matches": recommended_matches}
        self.redis_db.publish(f"{self.redis_channels_prefix}/recommendations/", json.dumps(data))

    def request_offers_bids(self, filters: Dict = None):
        data = {"filters": filters}
        self.redis_db.publish(f"{self.redis_channels_prefix}/offers-bids/", json.dumps(data))

    def _on_offers_bids_response(self, data: Dict):
        self.on_offers_bids_response(data=data)

    def on_offers_bids_response(self, data: Dict):
        recommendations = []
        self.submit_matches(recommendations)

    def _on_match(self, data: Dict):
        self.on_matched_recommendations_response(data=data)

    def on_matched_recommendations_response(self, data: Dict):
        pass

    def _on_tick(self, data: Dict):
        self.on_tick(data=data)

    def _on_market_cycle(self, data: Dict):
        self.on_market_cycle(data=data)

    def _on_finish(self, data: Dict):
        self.on_finish(data=data)

    def _on_event_or_response(self, payload: Dict):
        data = json.loads(payload["data"])
        self.executor.submit(self.on_event_or_response, data)
        # Call the corresponding event handler
        event = data.get("event")
        if hasattr(self, f"_on_{event}"):
            self.executor.submit(getattr(self, f"_on_{event}"), data)
