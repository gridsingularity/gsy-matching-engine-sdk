import json
import logging
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Dict

from gsy_framework.client_connections.utils import log_market_progression
from gsy_framework.utils import execute_function_util, wait_until_timeout_blocking
from redis import Redis

from gsy_matching_engine_sdk.constants import MAX_WORKER_THREADS
from gsy_matching_engine_sdk.matchers.matching_engine_matcher_client_interface import MatchingEngineMatcherClientInterface
from gsy_matching_engine_sdk.matchers.matching_engine_matcher_logger import MatchingEngineMatcherLogger


LOGGER = logging.getLogger(__name__)


class RedisBaseMatcher(MatchingEngineMatcherClientInterface):  # pylint: disable=too-many-instance-attributes
    """Handle order matching via redis connection."""
    def __init__(self, redis_url="redis://localhost:6379", pubsub_thread=None):
        self.simulation_id = None
        self.pubsub_thread = pubsub_thread
        self.redis_db = Redis.from_url(redis_url)
        self.pubsub = self.redis_db.pubsub() if pubsub_thread is None else pubsub_thread
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKER_THREADS)

        self.logger_helper = MatchingEngineMatcherLogger
        self._markets_cache = None  # Cached information about markets and time slots

        self._connect_to_simulation()

    def _connect_to_simulation(self):
        """Subscribe to redis response channels and thus connect to a simulation."""
        self._get_simulation_id(is_blocking=True)
        self.redis_channels_prefix = f"external-matching-engine/{self.simulation_id}"
        self._subscribe_to_response_channels()
        LOGGER.info("Connection to gsy-e has been established.")

    def _set_simulation_id(self, payload):
        data = json.loads(payload["data"])
        self.simulation_id = data.get("simulation_id")
        LOGGER.debug("Received Simulation ID %s", self.simulation_id)

    def _check_is_set_simulation_id(self):
        return self.simulation_id is not None

    def _start_pubsub_thread(self):
        if self.pubsub_thread is None:
            self.pubsub_thread = self.pubsub.run_in_thread(daemon=True)

    def _get_simulation_id(self, is_blocking=True):
        self.pubsub.subscribe(**{"external-matching-engine/simulation-id/response/":
                                 self._set_simulation_id})
        self._start_pubsub_thread()
        self.redis_db.publish("external-matching-engine/simulation-id/", json.dumps({}))

        if is_blocking:
            try:
                wait_until_timeout_blocking(self._check_is_set_simulation_id, timeout=50)
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
        LOGGER.debug("Sending recommendations %s", recommended_matches)
        data = {"recommended_matches": recommended_matches}
        self.redis_db.publish(f"{self.redis_channels_prefix}/recommendations/", json.dumps(data))

    def request_offers_bids(self, filters: Dict = None):
        data = {"filters": filters}
        self.redis_db.publish(f"{self.redis_channels_prefix}/offers-bids/", json.dumps(data))

    def request_area_id_name_map(self):
        """Request area_id_name_map from simulation."""
        channel = f"{self.simulation_id}/area-map/"
        self.redis_db.publish(channel, json.dumps({}))

    def _on_offers_bids_response(self, data: Dict):
        """Trigger actions when receiving the offers_bids_response event.

        Args:
            data: structure that maps each market UUID to a set of time slots. In each time slot
                are defined bids, offers, and other attributes relative to the slot. E.g.:
                {
                    "98015745-c5e7-4cb5-bce1-7738cb94c372": {
                        "2022-03-15T01:15": {
                            "bids": [], "offers": [], "market_type_name": "Spot Market"}
                        ...}
                }

        """
        self.on_offers_bids_response(data=data)

    def on_offers_bids_response(self, data: Dict):
        recommendations = []
        self.submit_matches(recommendations)

    def _on_match(self, data: Dict):
        self.logger_helper.log_recommendations_response(self._markets_cache, data)
        self.on_matched_recommendations_response(data=data)

    def on_matched_recommendations_response(self, data: Dict):
        pass

    def _on_tick(self, data: Dict):
        self._cache_markets_information(data)
        self.on_tick(data=data)

    def _on_market_cycle(self, data: Dict):
        self.on_market_cycle(data=data)

    def _on_finish(self, data: Dict):
        self.on_finish(data=data)

    def _on_area_map_response(self, data: Dict):
        self.on_area_map_response(data=data)

    def _on_event_or_response(self, payload: Dict):
        data = json.loads(payload["data"])
        log_market_progression(data)
        self.executor.submit(
            execute_function_util,
            function=lambda: self.on_event_or_response(data),
            function_name="on_event_or_response")

        # Call the corresponding event handler
        event = data.get("event")
        callback_function_name = f"_on_{event}"
        if hasattr(self, callback_function_name):
            callback_function = getattr(self, callback_function_name)
            self.executor.submit(
                execute_function_util,
                function=lambda: callback_function(data),
                function_name=callback_function_name)
