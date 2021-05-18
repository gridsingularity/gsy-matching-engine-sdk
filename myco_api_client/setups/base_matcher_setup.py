import os
from time import sleep

from myco_api_client.base_matcher import BaseMatcher


class MycoMatcher(BaseMatcher):
    pass

os.environ["API_CLIENT_USERNAME"] = ""
os.environ["API_CLIENT_PASSWORD"] = ""
matcher = MycoMatcher()
orders = matcher.request_orders()
while True:
    sleep(0.5)
