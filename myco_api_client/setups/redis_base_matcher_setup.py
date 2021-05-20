import logging
from time import sleep

from myco_api_client.redis_base_matcher import RedisBaseMatcher
from myco_api_client.utils import perform_pay_as_bid_match


class MycoMatcher(RedisBaseMatcher):
    def __init__(self, *args, **kwargs):
        super(MycoMatcher, self).__init__(*args, **kwargs)
        self.finished = False

    def on_market_cycle(self, data):
        logging.info(f"Market Cycle")

    def on_tick(self, data):
        logging.info(f"Tick")
        self.request_orders(filters={})

    def on_offers_bids_response(self, data):
        logging.info(f"Open offers/ bids response received {data}")
        recommendations = perform_pay_as_bid_match(data.get("market_offers_bids_list_mapping"))
        self.submit_matches(recommendations)

    def on_finish(self, data):
        self.finished = True

    def on_matched_recommendations_response(self, data):
        logging.info(f"Trades recommendations response returned {data}")

    def on_event_or_response(self, data):
        logging.info(f"Event arrived {data}")


matcher = MycoMatcher()

while not matcher.finished:
    sleep(.5)
