"""
Copyright 2018 Grid Singularity
This file is part of D3A.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import uuid

from d3a_interface.data_classes import Offer, BidOfferMatch, Bid
from pendulum import DateTime

from myco_api_client.matching_algorithms.preferred_partners_algorithm import (
    PreferredPartnersMatchingAlgorithm)


class TestPreferredPartnersMatchingAlgorithm:
    def test_perform_trading_partners_matching(self):
        bid = Bid(**{
            "id": uuid.uuid4(),
            "time": DateTime.now(),
            "price": 10,
            "energy": 30,
            "original_price": 8,
            "attributes": {},
            "requirements": [{"trading_partners": ["seller-1"]}],
            "buyer": "buyer"
        }).serializable_dict()
        offer = Offer(**{
            "id": uuid.uuid4(),
            "time": DateTime.now(),
            "price": 10,
            "energy": 30,
            "original_price": 8,
            "attributes": {},
            "requirements": [],
            "seller": "seller",
            "seller_id": "seller-1"
        }).serializable_dict()
        assert PreferredPartnersMatchingAlgorithm.perform_trading_partners_matching(
            market_id="market", bids=[bid], offers=[offer]) == [
                   BidOfferMatch(bids=[bid], offers=[offer],
                                 market_id="market",
                                 trade_rate=10 / 30,
                                 selected_energy=30).serializable_dict()]

    def test_get_energy_and_clearing_rate(self):
        offer = Offer(**{
            "id": uuid.uuid4(),
            "time": DateTime.now(),
            "price": 10,
            "energy": 30,
            "original_price": 8,
            "attributes": {},
            "requirements": [],
            "seller": "seller"
        })
        assert PreferredPartnersMatchingAlgorithm.get_energy_and_clearing_rate(
            offer_bid=offer.serializable_dict(), offer_bid_requirement={}
        ) == (30, 10 / 30)

        offer_bid_requirement = {"energy": 10, "price": 1}
        assert PreferredPartnersMatchingAlgorithm.get_energy_and_clearing_rate(
            offer_bid=offer.serializable_dict(), offer_bid_requirement=offer_bid_requirement
        ) == (10, 1)

    def test_get_actors_mapping(self):
        offers = [
            Offer(**{
                "id": f"id-{index}",
                "time": DateTime.now(),
                "price": 10,
                "energy": 30,
                "original_price": 8,
                "attributes": {},
                "requirements": [],
                "seller_id": f"seller_id-{index}",
                "seller": f"seller-{index}"
            }).serializable_dict() for index in range(3)
        ]
        assert PreferredPartnersMatchingAlgorithm.get_actors_mapping(offers) == {
            "seller_id-0": [offers[0]],
            "seller_id-1": [offers[1]],
            "seller_id-2": [offers[2]]}

    def test_can_bid_offer_be_matched(self):
        bid = Bid(**{
            "id": uuid.uuid4(),
            "time": DateTime.now(),
            "price": 10,
            "energy": 30,
            "original_price": 8,
            "attributes": {},
            "requirements": [{"energy_type": ["green"]}],
            "buyer": "buyer"
        }).serializable_dict()
        offer = Offer(**{
            "id": uuid.uuid4(),
            "time": DateTime.now(),
            "price": 10,
            "energy": 30,
            "original_price": 8,
            "attributes": {},
            "requirements": [],
            "seller": "seller"
        }).serializable_dict()
        assert PreferredPartnersMatchingAlgorithm.can_bid_offer_be_matched(
            bid=bid,
            offer=offer,
            bid_requirement=bid["requirements"][0],
            offer_requirement={}) is False

        offer["attributes"] = {"energy_type": "green"}
        assert PreferredPartnersMatchingAlgorithm.can_bid_offer_be_matched(
            bid=bid,
            offer=offer,
            bid_requirement=bid["requirements"][0],
            offer_requirement={}) is True

        offer["energy_rate"] = bid["energy_rate"] + 0.1
        assert PreferredPartnersMatchingAlgorithm.can_bid_offer_be_matched(
            bid=bid,
            offer=offer,
            bid_requirement=bid["requirements"][0],
            offer_requirement={}) is False
