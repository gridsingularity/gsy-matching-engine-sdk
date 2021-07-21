import logging

from d3a_interface.matching_algorithms import PayAsBidMatchingAlgorithm
from myco_api_client.matchers.redis_base_matcher import RedisBaseMatcher


class TestRedisMycoMatcher(RedisBaseMatcher):
    """Wrapper test class for the RedisBaseMatcher."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_finished = False
        self.errors = 0
        self.called_events = set()

    def on_market_cycle(self, data):
        self.called_events.add("market_cycle")
        logging.info("Market Cycle")

    def on_tick(self, data):
        self.called_events.add("tick")
        logging.info("Tick")
        self.request_offers_bids(filters={})

    def on_offers_bids_response(self, data):
        self.called_events.add("offers_bids_response")
        recommendations = PayAsBidMatchingAlgorithm.get_matches_recommendations(
            data.get("bids_offers"))
        self.submit_matches(recommendations)

    def on_finish(self, data):
        self.called_events.add("finish")
        self.is_finished = True

    def on_matched_recommendations_response(self, data):
        self.called_events.add("match")
        logging.info("Trades recommendations response returned", data)

    def on_event_or_response(self, data):
        self.called_events.add("event_or_response")
