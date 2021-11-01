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

from typing import Dict, List, Tuple

from d3a_interface.data_classes import BidOfferMatch, BaseBidOffer, Bid, Offer
from d3a_interface.matching_algorithms import BaseMatchingAlgorithm
from d3a_interface.matching_algorithms.requirements_validators import (
    RequirementsSatisfiedChecker)
from d3a_interface.utils import sort_list_of_dicts_by_attribute


class PreferredPartnersMatchingAlgorithm(BaseMatchingAlgorithm):
    """Perform PAB matching algorithm on bids trading partners.

    Match the bids with their preferred trading partners offers using the PAB matching algorithm.
    A trading partner is a preferable partner that should be matched with.
    """
    @classmethod
    def get_matches_recommendations(
            cls, matching_data: Dict) -> List[BidOfferMatch.serializable_dict]:
        recommendations = []
        for market_id, time_slot_data in matching_data.items():
            for time_slot, data in time_slot_data.items():
                if not (data.get("bids") and data.get("offers")):
                    continue

                recommendations.extend(cls.perform_trading_partners_matching(
                    market_id, time_slot, bids=data.get("bids"), offers=data.get("offers")))
        return recommendations

    @classmethod
    def perform_trading_partners_matching(
            cls, market_id: str,
            time_slot: str,
            bids: List[Bid.serializable_dict],
            offers: List[Offer.serializable_dict]) -> List[BidOfferMatch.serializable_dict]:
        """
        This is a variant of the PAB algorithm, it works as following:
            1. Iterate over bids
            2. Iterate over requirements of each bid
            3. Make sure there is a `trading_partners` requirement
            4. Iterate over trading partners
            5. Check if there are offers for each partner (from cache {seller_id: [sellers..]})
            6. Iterate over the requirements of the candidate offer
            7. Calculate the match's possible selection of energy and clearing rate
            8. Validate whether the offer/bid can satisfy each other's energy requirements
            9. Create a match recommendation
        """
        order_pairs = []
        bids = sort_list_of_dicts_by_attribute(bids, "energy_rate", True)
        offers = sort_list_of_dicts_by_attribute(offers, "energy_rate", True)
        offers_mapping = cls.get_actors_mapping(offers)
        already_selected_offers = set()
        for bid in bids:
            order_pair = None
            for bid_requirement in bid.get("requirements") or []:
                bid_required_energy, bid_required_clearing_rate = (
                    cls.get_energy_and_clearing_rate(bid, bid_requirement))
                preferred_offers = []
                for partner in bid_requirement.get("trading_partners") or []:
                    preferred_offers.extend(offers_mapping.get(partner) or [])
                for offer in preferred_offers:
                    if (offer.get("id") in already_selected_offers or
                            offer.get("seller") == bid.get("buyer")):
                        continue
                    for offer_requirement in offer.get("requirements") or [{}]:
                        if not cls.can_order_be_matched(
                                bid, offer, bid_requirement, offer_requirement):
                            continue

                        offer_required_energy, offer_required_clearing_rate = (
                            cls.get_energy_and_clearing_rate(offer, offer_requirement))

                        selected_energy = min(bid_required_energy, offer_required_energy)
                        already_selected_offers.add(offer.get("id"))
                        order_pair = (
                            BidOfferMatch(
                                market_id=market_id,
                                bids=[bid], offers=[offer],
                                selected_energy=selected_energy,
                                trade_rate=bid_required_clearing_rate,
                                time_slot=time_slot).serializable_dict())
                        break
                    if order_pair:
                        break
                if order_pair:
                    order_pairs.append(order_pair)
                    break

        return order_pairs

    @classmethod
    def can_order_be_matched(
            cls, bid: Bid.serializable_dict,
            offer: Offer.serializable_dict,
            bid_requirement: Dict, offer_requirement: Dict) -> bool:
        """Check if we can match offer & bid taking their requirements into consideration."""

        offer_required_energy, offer_required_clearing_rate = cls.get_energy_and_clearing_rate(
            offer, offer_requirement)

        bid_required_energy, bid_required_clearing_rate = cls.get_energy_and_clearing_rate(
            bid, bid_requirement)
        if bid_required_clearing_rate < offer_required_clearing_rate:
            return False
        if not (RequirementsSatisfiedChecker.is_bid_requirement_satisfied(
                bid=bid, offer=offer,
                selected_energy=min(offer_required_energy, bid_required_energy),
                clearing_rate=bid_required_clearing_rate,
                bid_requirement=bid_requirement) and
                RequirementsSatisfiedChecker.is_offer_requirement_satisfied(
                    bid=bid, offer=offer,
                    selected_energy=min(
                        offer_required_energy, bid_required_energy),
                    clearing_rate=bid_required_clearing_rate,
                    offer_requirement=offer_requirement)):
            return False
        return True

    @staticmethod
    def get_actors_mapping(
            bids_offers: List[BaseBidOffer.serializable_dict]
    ) -> Dict[str, List[BaseBidOffer.serializable_dict]]:
        """Map buyer/seller ids/origin ids to their offers or bids.

        Meant to only be used with input from the same type (Either offers or bids)
        """
        mapping = {}
        for order in bids_offers:
            # TODO: refactor Bid and Offer structures to homogenize id and origin selectors
            id_selector = "buyer_id" if order["type"] == "Bid" else "seller_id"
            origin_id_selector = (
                "buyer_origin_id" if order["type"] == "Bid" else "seller_origin_id")
            if order[id_selector]:
                if order[id_selector] not in mapping:
                    mapping[order[id_selector]] = []
                mapping[order[id_selector]].append(order)
            if (order[origin_id_selector]
                    and order[origin_id_selector] != order[id_selector]):
                if order[origin_id_selector] not in mapping:
                    mapping[order[origin_id_selector]] = []
                mapping[order[origin_id_selector]].append(order)
        return mapping

    @classmethod
    def get_energy_and_clearing_rate(
            cls, order: BaseBidOffer.serializable_dict,
            order_requirement: Dict) -> Tuple[float, float]:
        """Determine the energy and clearing rate based on an order + its requirement.

        A bid or offer can have energy and clearing rate attributes on both the instance
        and as a special requirement.
        The values in requirement have higher priority in selecting the energy and rate.

        Args:
            order: a serialized offer or bid structures
            order_requirement: specified requirement dictionary for the order
        """
        order_required_energy = order_requirement.get("energy") or order["energy"]
        order_required_clearing_rate = (
                order_requirement.get("price") or order["energy_rate"])
        return order_required_energy, order_required_clearing_rate
