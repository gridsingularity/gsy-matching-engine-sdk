import json
import logging
from concurrent.futures.thread import ThreadPoolExecutor

from d3a_interface.utils import wait_until_timeout_blocking
from redis import StrictRedis


from myco_api_client import MycoMatcherClientInterface
from myco_api_client.constants import MAX_WORKER_THREADS


class RedisAPIException(Exception):
    pass


class RedisBaseMatcher(MycoMatcherClientInterface):
    def __init__(self, redis_url='redis://localhost:6379',
                 pubsub_thread=None):
        self.job_uuid = None
        self.redis_db = StrictRedis.from_url(redis_url)
        self.pubsub = self.redis_db.pubsub() if pubsub_thread is None else pubsub_thread
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKER_THREADS)
        self._get_job_uuid(is_blocking=True)
        self.redis_channels_prefix = f"external-myco/{self.job_uuid}"
        self._subscribe_to_response_channels(pubsub_thread)

    def _set_job_uuid(self, payload):
        data = json.loads(payload["data"])
        self.job_uuid = data.get("job_uuid")
        logging.debug(f"Received JOB UUID {self.job_uuid}")

    def _check_is_set_job_uuid(self):
        return self.job_uuid is not None

    def _get_job_uuid(self, is_blocking=True):
        self.pubsub.subscribe(**{"external-myco/get_job_uuid/response": self._set_job_uuid})
        self.pubsub.run_in_thread(daemon=True)
        self.redis_db.publish("external-myco/get_job_uuid", json.dumps({}))

        if is_blocking:
            try:
                wait_until_timeout_blocking(
                    lambda: self._check_is_set_job_uuid(), timeout=50
                )
            except AssertionError:
                raise RedisAPIException(f'API registration process timed out.')

    def _subscribe_to_response_channels(self, pubsub_thread=None):
        channel_subs = {
            f"{self.redis_channels_prefix}/response/events/":
                self._events_callback_dict,
            f"{self.redis_channels_prefix}/response/get_offers_bids/":
                self._on_offers_bids_response,
            f"{self.redis_channels_prefix}/response/matched_recommendations/":
                self._on_match,
            f"{self.redis_channels_prefix}/response/*": self._on_event_or_response
        }
        self.pubsub.psubscribe(**channel_subs)
        if pubsub_thread is None:
            self.pubsub.run_in_thread(daemon=True)

    def _events_callback_dict(self, message):
        data = json.loads(message["data"])
        event = data.get("event")
        if hasattr(self, f"_on_{event}"):
            getattr(self, f"_on_{event}")(data)

    def submit_matches(self, recommended_matches):
        logging.debug(f"Sending recommendations {recommended_matches}")
        data = {"recommended_matches": recommended_matches}
        self.redis_db.publish(f"{self.redis_channels_prefix}/post_recommendations/", json.dumps(data))

    def request_orders(self, filters=None):
        data = {"filters": filters}
        self.redis_db.publish(f"{self.redis_channels_prefix}/get_offers_bids/", json.dumps(data))

    def _on_offers_bids_response(self, payload):
        data = json.loads(payload["data"])
        self.executor.submit(self.on_offers_bids_response, data=data)

    def on_offers_bids_response(self, data):
        recommendations = []
        self.submit_matches(recommendations)

    def _on_match(self, payload):
        data = json.loads(payload["data"])
        self.executor.submit(self.on_matched_recommendations_response, data=data)

    def on_matched_recommendations_response(self, data):
        pass

    def _on_tick(self, data):
        self.executor.submit(self.on_tick, data=data)

    def _on_market(self, data):
        self.executor.submit(self.on_market_cycle, data=data)

    def _on_finish(self, data):
        self.executor.submit(self.on_finish, data=data)

    def _on_event_or_response(self, payload):
        data = json.loads(payload["data"])
        self.executor.submit(self.on_event_or_response, data)
