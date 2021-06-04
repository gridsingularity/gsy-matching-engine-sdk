import logging

from myco_api_client.redis_base_matcher import RedisBaseMatcher
from d3a_interface.utils import perform_pay_as_bid_match


class TestRedisMycoMatcher(RedisBaseMatcher):
    def __init__(self, *args, **kwargs):
        super(TestRedisMycoMatcher, self).__init__(*args, **kwargs)
        self.is_finished = False
        self.errors = 0
        self.called_events = set()

    def on_market_cycle(self, data):
        self.called_events.add("market")
        logging.info(f"Market Cycle")

    def on_tick(self, data):
        self.called_events.add("tick")
        logging.info(f"Tick")
        self.request_orders(filters={})

    def on_offers_bids_response(self, data):
        self.called_events.add("offers_bids_response")
        logging.info(f"Open offers/ bids response received {data}")
        recommendations = perform_pay_as_bid_match(data.get("market_offers_bids_list_mapping"))
        self.submit_matches(recommendations)

    def on_finish(self, data):
        self.called_events.add("finish")
        self.is_finished = True

    def on_matched_recommendations_response(self, data):
        self.called_events.add("match")
        logging.info(f"Trades recommendations response returned {data}")

    def on_event_or_response(self, data):
        self.called_events.add("event_or_response")
