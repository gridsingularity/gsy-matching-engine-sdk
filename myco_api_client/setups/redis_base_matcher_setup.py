import logging
from time import sleep

from myco_api_client.redis_base_matcher import RedisBaseMatcher
from d3a_interface.utils import perform_pay_as_bid_match


class RedisMycoMatcher(RedisBaseMatcher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_finished = False
        self.errors = 0

    def on_market_cycle(self, data):
        pass

    def on_tick(self, data):
        self.request_offers_bids(filters={})

    def on_offers_bids_response(self, data):
        recommendations = perform_pay_as_bid_match(data.get("market_offers_bids_list_mapping"))
        if recommendations:
            self.submit_matches(recommendations)

    def on_finish(self, data):
        self.is_finished = True

    def on_matched_recommendations_response(self, data):
        pass

    def on_event_or_response(self, data):
        logging.info("Event arrived %s", data)


matcher = RedisMycoMatcher()

while not matcher.is_finished:
    sleep(.5)
