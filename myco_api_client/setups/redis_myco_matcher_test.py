import logging
from time import sleep

from myco_api_client.matchers.redis_base_matcher import RedisBaseMatcher
from myco_api_client.matching_algorithms import AttributedMatchingAlgorithm
from d3a_interface.matching_algorithms.pay_as_clear_matching_algorithm import \
    PayAsClearMatchingAlgorithm
from d3a_interface.matching_algorithms.pay_as_bid_matching_algorithm import \
    PayAsBidMatchingAlgorithm


# from tabulate import tabulate

class RedisMycoMatcher(RedisBaseMatcher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_finished = False
        self.errors = 0

    def on_market_cycle(self, data):
        print()
        print("New market slot")
        print()

    def on_tick(self, data):
        print()
        print("Request offers and bids")
        print()

        self.request_offers_bids(
            filters={})  # TODO: request filtered bids / offers by specifying the "market_id" (Filters functionality currently not working) - in this way we request the data at each tick (synchronous)

    def on_offers_bids_response(self, data):

        matching_data = data.get(
            "bids_offers")  # Receive all the bids/offers of all the assets from the order book - the matching data have the attributes

        if not matching_data:
            return

        # With the current implementation, the matching algorithm is triggered at each tick
        recommendations = PayAsBidMatchingAlgorithm.get_matches_recommendations(
            matching_data)  # TODO: use your own matching algorithm (parenthesis are needed when using the template Pay-as-Clear)

        if recommendations:  # Most of the times recommenations are empty - just at the 8th / 9th tick they start to be non empty

            # print("Recommendations:", recommendations)

            for i in range(len(recommendations)):

                print()
                print("RECOMMENDATION ", i + 1)
                print()
                list_bids = recommendations[i]['bids']
                list_offers = recommendations[i]['offers']
                for j in range(len(list_bids)):
                    print("Type: ", list_bids[j]['type'])
                    print("ID:", list_bids[j]['id'])
                    print("Time: ", list_bids[j]['time'])
                    print("Energy: ", list_bids[j]['energy'])
                    print("Energy rate: ", list_bids[j]['energy_rate'])
                    print("Buyer origin: ", list_bids[j]['buyer_origin'])
                    print("Buyer: ", list_bids[j]['buyer'])
                    print("Attributes: ", list_bids[j]['attributes'])
                    print("Requirements: ", list_bids[j]['requirements'])
                    print()

                for j in range(len(list_offers)):
                    print("Type: ", list_offers[j]['type'])
                    print("ID:", list_offers[j]['id'])
                    print("Time: ", list_offers[j]['time'])
                    print("Energy: ", list_offers[j]['energy'])
                    print("Energy rate: ", list_offers[j]['energy_rate'])
                    print("Seller origin: ", list_offers[j]['seller_origin'])
                    print("Seller: ", list_offers[j]['seller'])
                    print("Attributes: ", list_offers[j]['attributes'])
                    print("Requirements: ", list_offers[j]['requirements'])
                    print()

            logging.info("Submitting %s recommendations.", len(recommendations))
            self.submit_matches(
                recommendations)  # Post matched bid / offer pairs back to the Grid Singularity energy exchange

    def on_finish(self, data):
        self.is_finished = True

    def on_matched_recommendations_response(self,
                                            data):  # Triggered when the posted recommendations response is returned
        pass

    def on_event_or_response(self,
                             data):  # Triggered each time an event arrives or any response (from sending the batch commands such as trades confirmations) is triggered
        pass
        # logging.info("Event arrived %s", data)


matcher = RedisMycoMatcher()

while not matcher.is_finished:
    sleep(.5)
