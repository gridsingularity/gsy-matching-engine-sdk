from time import sleep

from myko_api_client.base_matcher import BaseMatcher


class MykoMatcher(BaseMatcher):
    pass

import os
os.environ["API_CLIENT_USERNAME"] = "dev@gridsingularity.com"
os.environ["API_CLIENT_PASSWORD"] = "8gcBB9D5sK"
matcher = MykoMatcher()
orders = matcher.request_orders()
while True:
    sleep(0.5)
