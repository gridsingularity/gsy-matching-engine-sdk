import logging
import os
from time import sleep

from gsy_framework.matching_algorithms import AttributedMatchingAlgorithm

from gsy_matching_engine_sdk.matchers import RedisBaseMatcher
from gsy_matching_engine_sdk.matchers.rest_base_matcher import RestBaseMatcher

if os.environ["MATCHING_ENGINE_RUN_ON_REDIS"] == "true":
    BaseMatcher = RedisBaseMatcher
else:
    BaseMatcher = RestBaseMatcher


class MatchingEngineMatcher(BaseMatcher):
    """Class that demonstrates how to override and add functionality to the MatchingEngine Matcher."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_finished = False
        self.request_area_id_name_map()
        self.id_list = []

    def on_area_map_response(self, data):
        market_list = ["Community"]
        for market in market_list:
            for market_id, name in data["area_mapping"].items():
                if name == market:
                    self.id_list.append(market_id)

    def on_market_cycle(self, data):
        pass

    def on_tick(self, data):
        self.request_offers_bids(filters={"markets": self.id_list})

    def on_offers_bids_response(self, data):
        matching_data = data.get("bids_offers")
        if not matching_data:
            return
        recommendations = AttributedMatchingAlgorithm.get_matches_recommendations(
            matching_data
        )
        if recommendations:
            self.submit_matches(recommendations)

    def on_matched_recommendations_response(self, data):
        logging.info("Trades recommendations response returned %s", data)

    def on_event_or_response(self, data):
        pass

    def on_finish(self, data):
        self.is_finished = True


matcher = MatchingEngineMatcher()

while not matcher.is_finished:
    sleep(0.5)
