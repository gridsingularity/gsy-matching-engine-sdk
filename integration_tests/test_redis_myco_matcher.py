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
        self.request_area_id_name_map()

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

    def on_area_map_response(self, data):
        area_set = {"Grid", "House 1", "H1 General Load1", "H1 General Load2",
                     "H1 Storage1", "H1 Storage2", "H1 PV1", "H1 PV2",
                     "House 2", "H2 General Load1", "H2 Storage1", "H2 PV", "Cell Tower",
                     "Market Maker"}
        if not (data.get("area_map") and list(data["area_map"].values()) == area_set):
            self.errors += 1
        self.called_events.add("on_area_map_response")
