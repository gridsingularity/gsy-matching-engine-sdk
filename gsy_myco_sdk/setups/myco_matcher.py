import os
from time import sleep

from gsy_framework.matching_algorithms import AttributedMatchingAlgorithm

from gsy_myco_sdk.matchers import RedisBaseMatcher
from gsy_myco_sdk.matchers.rest_base_matcher import RestBaseMatcher

from gsy_myco_sdk.utils import log_recommendations_response

if os.environ["MYCO_CLIENT_RUN_ON_REDIS"] == "true":
    BaseMatcher = RedisBaseMatcher
else:
    BaseMatcher = RestBaseMatcher


class MycoMatcher(BaseMatcher):
    """Class that demonstrates how to override and add functionality to the Myco Matcher."""

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
        log_recommendations_response(data)

    def on_event_or_response(self, data):
        pass

    def on_finish(self, data):
        self.is_finished = True


matcher = MycoMatcher()

while not matcher.is_finished:
    sleep(0.5)
