import logging
import os
from time import sleep

from gsy_myco_sdk.matchers import RedisBaseMatcher
from gsy_myco_sdk.matchers.base_matcher import BaseMatcher
from gsy_myco_sdk.matching_algorithms import AttributedMatchingAlgorithm

if os.environ["MYCO_CLIENT_RUN_ON_REDIS"] == "true":
    base_matcher = RedisBaseMatcher
else:
    base_matcher = BaseMatcher


class MycoMatcher(base_matcher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_finished = False

    def on_market_cycle(self, data):
        pass

    def on_tick(self, data):
        self.request_offers_bids(filters={})

    def on_offers_bids_response(self, data):
        matching_data = data.get("bids_offers")
        if not matching_data:
            return
        recommendations = AttributedMatchingAlgorithm.get_matches_recommendations(
            matching_data)
        if recommendations:
            logging.info("Submitting %s recommendations.", len(recommendations))
            self.submit_matches(recommendations)

    def on_finish(self, data):
        self.is_finished = True

    def on_matched_recommendations_response(self, data):
        pass

    def on_event_or_response(self, data):
        logging.debug("Event arrived %s", data)


matcher = MycoMatcher()

while not matcher.is_finished:
    sleep(0.5)
