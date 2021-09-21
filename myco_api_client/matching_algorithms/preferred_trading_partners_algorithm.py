from typing import Dict, List

from d3a_interface.data_classes import BidOfferMatch
from d3a_interface.matching_algorithms import BaseMatchingAlgorithm
from d3a_interface.matching_algorithms.requirements_validators import (
    RequirementsSatisfiedChecker)
from d3a_interface.utils import sort_list_of_dicts_by_attribute


class PreferredPartnersMatchingAlgorithm(BaseMatchingAlgorithm):
    @classmethod
    def get_matches_recommendations(
            cls, matching_data: Dict) -> List[BidOfferMatch.serializable_dict]:
        for market_id, data in matching_data.items():
            if not (data.get("bids") and data.get("offers")):
                continue
            bids = sort_list_of_dicts_by_attribute(data["bids"], "energy", True)
            offers = sort_list_of_dicts_by_attribute(data["offers"], "energy", True)

            recommendations = cls._match_preferred_partners(
                market_id, bids=bids, offers=offers)
            return recommendations

    @classmethod
    def _match_preferred_partners(cls, market_id, bids, offers):
        bid_offer_pairs = []
        offers_mapping = cls._get_mapping(offers)
        already_selected_offers = set()
        for bid in bids.values():
            bid_offer_pair = None
            for bid_requirement in bid.get("requirements") or []:
                bid_required_energy, bid_required_clearing_rate = (
                    cls._get_energy_and_clearing_rate(bid, bid_requirement))
                preferred_offers = list(
                    offer for offer in offers_mapping.get(partner)
                    for partner in bid_requirement.get("trading_partners") or []
                )
                for offer in preferred_offers:
                    if (offer.get("id") in already_selected_offers or
                            offer.get("seller") == bid.get("buyer")):
                        continue
                    for offer_requirement in offer.get("requirements") or [{}]:
                        if not cls._are_bid_and_offer_requirements_satisfied(
                                bid=bid, offer=offer,
                                offer_requirement=offer_requirement,
                                bid_requirement=bid_requirement
                        ):
                            continue
                        offer_required_energy, offer_required_clearing_rate = (
                            cls._get_energy_and_clearing_rate(offer, offer_requirement))
                        already_selected_offers.add(offer.get("id"))
                        selected_energy = min(bid_required_energy, offer_required_energy)
                        bid_offer_pair = (
                            BidOfferMatch(
                                market_id=market_id,
                                bids=[bid], offers=[offer],
                                selected_energy=selected_energy,
                                trade_rate=bid_required_clearing_rate).serializable_dict())
                        break
                    if bid_offer_pair:
                        break
                if bid_offer_pair:
                    bid_offer_pairs.append(bid_offer_pair)
                    break

        return bid_offer_pairs

    @classmethod
    def _are_bid_and_offer_requirements_satisfied(
            cls, bid, offer, bid_requirement, offer_requirement):
        offer_required_energy, offer_required_clearing_rate = cls._get_energy_and_clearing_rate(
            offer, offer_requirement)

        bid_required_energy, bid_required_clearing_rate = cls._get_energy_and_clearing_rate(
            bid, bid_requirement)
        if not cls._is_valid_clearing_rate(
                offer_clearing_rate=offer_required_clearing_rate,
                bid_clearing_rate=bid_required_clearing_rate):
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
    def _get_mapping(bids_offers):
        mapping = {}
        for bid_offer in bids_offers:
            # TODO: refactor Bid and Offer structures to homogenize id and origin selectors
            id_selector = "buyer_id" if bid_offer["type"] == "Bid" else "seller_id"
            origin_id_selector = (
                "buyer_origin_id" if bid_offer["type"] == "Bid" else "seller_origin_id")
            if bid_offer[id_selector] not in mapping:
                mapping[bid_offer[id_selector]] = []
            if bid_offer[origin_id_selector] not in mapping:
                mapping[bid_offer[origin_id_selector]] = []

            mapping[bid_offer[id_selector]].append(bid_offer)
            mapping[bid_offer[origin_id_selector]].append(bid_offer)
        return mapping

    @classmethod
    def _get_energy_and_clearing_rate(cls, offer_bid, offer_bid_requirement):
        offer_bid_required_energy = offer_bid_requirement.get("energy") or offer_bid["energy"]
        offer_bid_required_clearing_rate = (
                offer_bid_requirement.get("price") or offer_bid["energy_rate"])
        return offer_bid_required_energy, offer_bid_required_clearing_rate

    @staticmethod
    def _is_valid_clearing_rate(offer_clearing_rate, bid_clearing_rate):
        return offer_clearing_rate <= bid_clearing_rate
