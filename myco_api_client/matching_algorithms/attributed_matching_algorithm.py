from copy import deepcopy
from typing import Dict, Union, List, Tuple

from d3a_interface.dataclasses import BidOfferMatch
from d3a_interface.matching_algorithms import BaseMatchingAlgorithm, PayAsBidMatchingAlgorithm


# TODO: Implement step 1 of the algorithm + add tests
class AttributedMatchingAlgorithm(BaseMatchingAlgorithm):
    """Perform attributed bid offer matching using pay as bid algorithm.

    The algorithm aggregates related offers/bids based on the following:
        1. Preferred trading partner.
        2. Green tagged energy.
        3. All unmatched yet.

    Aggregated lists will be matched with the pay_as_bid algorithm.
    """

    @classmethod
    def get_matches_recommendations(
            cls, matching_data: Dict[str, Dict]) -> List[BidOfferMatch.serializable_dict]:
        recommendations = []
        for market_id, data in matching_data.items():
            bids_mapping = {bid["id"]: bid for bid in data.get("bids")}
            offers_mapping = {offer["id"]: offer for offer in data.get("offers")}

            if not (bids_mapping and offers_mapping):
                continue

            green_offers = cls._filter_offers_bids_by_attribute(
                list(offers_mapping.values()), "energy_type", "PV")
            green_bids = cls._filter_offers_bids_by_requirement(
                list(bids_mapping.values()), "energy_type", "PV")
            green_recommendations = PayAsBidMatchingAlgorithm.get_matches_recommendations(
                    {market_id: {"bids": green_bids, "offers": green_offers}})
            recommendations.extend(green_recommendations)
            bids_mapping, offers_mapping = cls._filter_open_bids_offers(
                bids_mapping, offers_mapping, green_recommendations)
            residual_recommendations = PayAsBidMatchingAlgorithm.get_matches_recommendations(
                    {market_id: {
                        "bids": list(bids_mapping.values()),
                        "offers": list(offers_mapping.values())}})
            recommendations.extend(residual_recommendations)

        return recommendations

    @classmethod
    def _filter_offers_bids_by_requirement(
            cls, offers_bids: List[Dict], requirement_key: str,
            requirement_value: Union[str, int, float]) -> List[Dict]:
        """Return a list of offers or bids which have a requirement == specified value."""
        filtered_list = []
        for offer_bid in offers_bids:
            for requirement in offer_bid.get("requirements") or []:
                if requirement_key not in requirement:
                    continue
                if (isinstance(requirement.get(requirement_key), list)
                        and requirement_value in requirement.get(requirement_key)
                        or requirement_value == requirement.get(requirement_key)):
                    filtered_list.append(offer_bid)
                    break
        return filtered_list

    @classmethod
    def _filter_offers_bids_by_attribute(
            cls, offers_bids: list, attribute_key: str,
            attribute_value: Union[str, int, float]) -> List[Dict]:
        """Return a list of offers or bids which have an attribute == specified value."""
        filtered_list = []
        for offer_bid in offers_bids:
            if attribute_key not in offer_bid.get("attributes") or {}:
                continue
            if (isinstance(offer_bid.attributes.get(attribute_key), list)
                    and attribute_value in offer_bid.attributes.get(attribute_key)
                    or attribute_value == offer_bid.attributes.get(attribute_key)):
                filtered_list.append(offer_bid)
        return filtered_list

    @classmethod
    def _filter_open_bids_offers(
            cls, bids_mapping: Dict[str, Dict], offers_mapping: Dict[str, Dict],
            recommendations: List[BidOfferMatch.serializable_dict]) -> Tuple[Dict, Dict]:
        """Return bids/offers lists that are not present in the recommendations yet."""
        open_bids_mapping = deepcopy(bids_mapping)
        open_offers_mapping = deepcopy(offers_mapping)
        for recommendation in recommendations:
            bid_id = recommendation["bid"]["id"]
            offer_id = recommendation["offer"]["id"]
            if bid_id in open_bids_mapping:
                open_bids_mapping.pop(bid_id)
            if offer_id in open_offers_mapping:
                open_offers_mapping.pop(offer_id)
        return open_bids_mapping, open_offers_mapping


def test_filter_offers_bids_have_requirement(
        offers_bids: list, requirement_key: str, requirement_value: Union[str, int, float]):
    return AttributedMatchingAlgorithm._filter_offers_bids_by_requirement(
        offers_bids, requirement_key, requirement_value)
