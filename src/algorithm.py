#!/usr/bin/env python3

import random
from collections import Counter
from enum import Enum, auto, unique, Flag
from itertools import chain
from typing import *
from urllib.parse import ParseResult

K = TypeVar('K')
V = TypeVar('V')


def zip_dict(*dictionaries: Mapping[K, V]) -> Iterator[Sequence[Union[K, V]]]:
    """
    Like ``zip(*(dict_item.items() for dict_item in dict_list))``,
    except each iteration value is grouped by the same dict key

    :param dictionaries: The dicts to zip
    :return: (key, value1, value2, ...)
    """
    try:
        first_dict, *other_dicts = dictionaries
    except ValueError:
        yield from ()
    else:
        common_keys: Set[K] = set(first_dict.keys())
        common_keys.intersection(*other_dicts)

        for common_key in common_keys:
            yield (common_key, *(dict_item[common_key] for dict_item in dictionaries))


CardId = str
Deck = Counter[CardId]


@unique
class ManaColor(Enum):
    ANY = auto()
    WHITE = auto()
    BLUE = auto()
    BLACK = auto()
    RED = auto()
    GREEN = auto()
    COLORLESS = auto()
    SNOW = auto()


@unique
class Keyword(Flag):
    DEATHTOUCH = auto()
    DEFENDER = auto()
    DOUBLE_STRIKE = auto()
    ENCHANT = auto()
    EQUIP = auto()
    FIRST_STRIKE = auto()
    FLASH = auto()
    FLYING = auto()
    HASTE = auto()
    HEXPROOF = auto()
    INDESTRUCTIBLE = auto()
    LIFELINK = auto()
    MENACE = auto()
    PROWESS = auto()
    REACH = auto()
    SCRY = auto()
    TRAMPLE = auto()
    VIGILANCE = auto()


@unique
class Archetype(Flag):
    BOMB = auto()
    REMOVAL = auto()
    COMBAT_TRICK = auto()
    EVASIVE = auto()
    COUNTER = auto()
    CARD_DRAW = auto()
    MANA_FIXING = auto()


@unique
class CardType(Enum):
    LAND = auto()
    ENCHANTMENT = auto()
    ARTIFACT = auto()
    PLANESWALKER = auto()
    CREATURE = auto()
    SORCERY = auto()


class Land(NamedTuple):
    color: ManaColor


class Enchantment(NamedTuple):
    possible_target_types: FrozenSet[CardType]


class Artifact(NamedTuple):
    pass


class Planeswalker(NamedTuple):
    loyalty: int
    # Actions with loyalty effects
    actions: Sequence[int]


class Creature(NamedTuple):
    power: int
    toughness: int
    keywords: Keyword


class Sorcery(NamedTuple):
    pass


class Instant(NamedTuple):
    pass


class Rarity(Enum):
    COMMON = BLACK = auto()
    UNCOMMON = GRAY = auto()
    RARE = YELLOW = auto()
    MYTHIC_RARE = RED = auto()


class Card(NamedTuple):
    name: str
    mana_cost: Mapping[ManaColor, int]
    converted_mana_cost: int
    type_info: Union[Land, Enchantment, Artifact, Planeswalker, Creature, Sorcery, Instant]
    set: str
    rarity: Rarity
    rating: int
    guild: Optional[str]
    image_url: ParseResult
    archetypes: Archetype


def generate_booster_packs(card_options: Sequence[CardId], length: int = 90) -> Iterable[Deck]:
    while True:
        cards: List[CardId] = random.choices(card_options, k=length)
        yield Counter(cards)


def evaluate_deck(deck: Deck, set_info: Mapping[CardId, Card]) -> float:
    """
    :return: A penalty value which should be minimized
    """
    # Deck size
    deck_elements = tuple(deck.elements())
    number_of_cards_penalty = (40 - len(deck_elements)) ** 2

    # Mana curve

    # Land percentage
    land_counts = Counter(set_info[card_id].type_info.color
                          for card_id in deck_elements
                          if isinstance(set_info[card_id].type_info, Land))
    total_lands = sum(land_counts.values())
    land_ratios: Dict[ManaColor, float] = {color: count / total_lands
                                           for color, count in land_counts.items()}

    total_land_ratio = total_lands / len(deck_elements)
    land_ratio_penalty = 0 if 16 / 40 <= total_land_ratio <= 18 / 40 else abs(17 / 40 - total_land_ratio)

    # Land color percentage
    mana_costs: Iterator[Mapping[ManaColor, int]] = chain(*(set_info[card_id].mana_cost for card_id in deck_elements))
    mana_symbol_counts = Counter(color
                                 for mana_cost in mana_costs
                                 for color, quantity in mana_cost.items()
                                 for _ in range(quantity))
    total_mana_symbols = sum(mana_symbol_counts.values())
    mana_symbol_ratios: Dict[ManaColor, float] = {color: count / total_mana_symbols
                                                  for color, count in mana_symbol_counts.items()}

    mana_symbol_ratio_penalty: float = sum(abs(mana_symbol_ratio - land_ratio)
                                           for _, mana_symbol_ratio, land_ratio
                                           in zip_dict(mana_symbol_ratios, land_ratios))

    # Color identity
    dominant_mana_colors: Set[ManaColor] = {mana_color
                                            for mana_color, ratio in mana_symbol_ratios.items()
                                            if ratio >= 0.05}
    splash_mana_colors = set(mana_symbol_ratios.keys()) - dominant_mana_colors
    deck_color_penalty = max(2 - len(dominant_mana_colors), 2) + len(splash_mana_colors)

    # Card archetypes
    bomb_count = Counter(set_info[card_id].archetypes
                         for card_id in deck_elements
                         if set_info[card_id].archetypes.BOMB)
    removal_count = Counter(set_info[card_id].archetypes
                         for card_id in deck_elements
                         if set_info[card_id].archetypes.REMOVAL)
    evasive_count = Counter(set_info[card_id].archetypes
                         for card_id in deck_elements
                         if set_info[card_id].archetypes.EVASIVE)
    duds_count = Counter(set_info[card_id].archetypes
                         for card_id in deck_elements
                         if set_info[card_id].rating <= 1)
    manafix_count = Counter(set_info[card_id].archetypes
                         for card_id in deck_elements
                         if set_info[card_id].archetypes.MANA_FIXING)

    archetype_penalties = 0
    archetype_penalties += (0 if bomb_count >= 1 else 10) + (0 if removal_count >= 2 else 10 * (2 - removal_count))

    # Combine objectives
    total_penalty = number_of_cards_penalty + land_ratio_penalty + mana_symbol_ratio_penalty + deck_color_penalty

    return total_penalty


if __name__ == '__main__':
    import argparse
    import csv

    parser = argparse.ArgumentParser(description='Compute an optimal deck given a set of booster packs')
    parser.add_argument('ratings-file', metavar='RATING', type=argparse.FileType('r'),
                        help='The ratings list as a CSV')

    cards: Dict[CardId, Card] = {}

    args = parser.parse_args()
    with args.ratings_file as ratings_file:
        ratings: Iterator[List[str]] = csv.reader(ratings_file)
        _ = next(ratings)  # Skip header row
        for rating in ratings:
            card_id, card_name, mana_cost, cmc, card_type, rarity, guild, \
                bomb, removal, combat_trick, evasive, counter, card_draw, mana_fixing, card_set, image_url = rating
            # card = Card(name=card_name, mana_cost=mana_cost, converted_mana_cost=cmc, type=card_type)
            # cards[card_id] = card
