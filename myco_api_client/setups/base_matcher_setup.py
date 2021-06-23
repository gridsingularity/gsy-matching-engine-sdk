import logging
from time import sleep

from myco_api_client.base_matcher import BaseMatcher
from d3a_interface.utils import perform_pay_as_bid_match


class MycoMatcher(BaseMatcher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_finished = False

    def on_market_cycle(self, data):
        pass

    def on_tick(self, data):
        self.request_offers_bids(filters={})

    def on_offers_bids_response(self, data):
        recommendations = perform_pay_as_bid_match(data.get("orders"))
        logging.error("Submitting %s recommendations.", len(recommendations))
        if recommendations:
            self.submit_matches(recommendations)

    def on_finish(self, data):
        self.is_finished = True

    def on_matched_recommendations_response(self, data):
        pass

    def on_event_or_response(self, data):
        logging.info("Event arrived %s", data)


matcher = MycoMatcher()

while not matcher.is_finished:
    sleep(0.5)
