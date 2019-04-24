#!/usr/bin/env python3

"""
Magic: The Gathering Tournament Deck Optimizer
"""

import random
from collections import Counter, defaultdict
from enum import Enum, auto, unique
from typing import *
from urllib.parse import ParseResult

K = TypeVar('K')
V = TypeVar('V')


def zip_dict(*dictionaries: Mapping[K, V]) -> Iterator[Tuple[K, Iterator[K, V]]]:
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
            yield common_key, (dict_item[common_key] for dict_item in dictionaries)


Index = int
Count = int

CardId = str
CardFaceId = Tuple[CardId, Index]
Deck = Mapping[CardId, Count]


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
class Keyword(Enum):
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
class Archetype(Enum):
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
    possible_target_types: AbstractSet[CardType]


class Artifact(NamedTuple):
    pass


class Planeswalker(NamedTuple):
    loyalty: int
    # Actions with loyalty effects
    actions: Sequence[int]


class Creature(NamedTuple):
    power: int
    toughness: int
    keywords: AbstractSet[Keyword]


class Sorcery(NamedTuple):
    pass


class Instant(NamedTuple):
    pass


class Rarity(Enum):
    COMMON = BLACK = 'Common'
    UNCOMMON = GRAY = 'Uncommon'
    RARE = YELLOW = 'Rare'
    MYTHIC_RARE = RED = 'Mythic'


class CardFace(NamedTuple):
    name: str
    mana_cost: Mapping[ManaColor, Count]
    converted_mana_cost: int
    type: CardType


class Card(NamedTuple):
    faces: Sequence[CardFace]
    set: str
    rarity: Rarity
    rating: int
    guild: Optional[str]
    image_url: ParseResult
    archetypes: AbstractSet[Archetype]


class CardTypes(NamedTuple):
    lands: Mapping[CardFaceId, Land]
    enchantments: Mapping[CardFaceId, Enchantment]
    artifacts: Mapping[CardFaceId, Artifact]
    planeswalkers: Mapping[CardFaceId, Planeswalker]
    creatures: Mapping[CardFaceId, Creature]
    sorceries: Mapping[CardFaceId, Sorcery]
    instants: Mapping[CardFaceId, Instant]


class SetInfo(NamedTuple):
    cards: Mapping[CardId, Card]
    card_types: CardTypes


def generate_booster_packs(card_options: Sequence[CardId], length: int = 90) -> Iterable[Deck]:
    """
    Generates a booster pack from the given card options (repetition is allowed)

    :param card_options: The cards to choose from
    :param length: The length of the booster pack
    :return: The booster pack
    """
    while True:
        cards: List[CardId] = random.choices(card_options, k=length)
        yield Counter(cards)


def evaluate_deck(deck: Deck, set_info: SetInfo) -> float:
    """
    :return: A penalty value which should be minimized
    """
    cards = set_info.cards
    lands = set_info.card_types.lands

    # Deck counts
    total_cards: int = 0
    land_counts: DefaultDict[ManaColor, int] = defaultdict(int)
    mana_symbol_counts: DefaultDict[ManaColor, int] = defaultdict(int)
    archetype_counts: DefaultDict[Archetype, int] = defaultdict(int)
    duds_count: int = 0

    for card_id, card_quantity in deck.items():
        card = cards[card_id]

        # Total cards
        total_cards += card_quantity

        # Lands
        for face_index, _ in enumerate(card.faces):
            try:
                mana_color = lands[card_id, face_index].color
            except KeyError:
                pass
            else:
                land_counts[mana_color] += card_quantity
                break  # Only count one land per card

        # Mana symbols
        for face in card.faces:
            for mana_color, mana_quantity in face.mana_cost:
                mana_symbol_counts[mana_color] += mana_quantity

        # Archetypes
        for archetype in card.archetypes:
            archetype_counts[archetype] += card_quantity

        # Duds
        if card.rating <= 1:
            duds_count += card_quantity

    # Evaluate deck size
    number_of_cards_penalty = (40 - total_cards) ** 2

    # TODO: Evaluate mana curve

    # Evaluate land percentage
    total_lands = sum(land_counts.values())
    land_ratios: Dict[ManaColor, float] = {color: count / total_lands
                                           for color, count in land_counts.items()}

    total_land_ratio = total_lands / total_cards
    land_ratio_penalty = 0 if 16 / 40 <= total_land_ratio <= 18 / 40 else abs(17 / 40 - total_land_ratio)

    # Evaluate land color percentage
    total_mana_symbols = sum(mana_symbol_counts.values())
    mana_symbol_ratios: Dict[ManaColor, float] = {color: count / total_mana_symbols
                                                  for color, count in mana_symbol_counts.items()}

    mana_symbol_ratio_penalty: float = sum(abs(mana_symbol_ratio - land_ratio)
                                           for _, (mana_symbol_ratio, land_ratio)
                                           in zip_dict(mana_symbol_ratios, land_ratios))

    # Evaluate color identity
    dominant_mana_colors: Set[ManaColor] = {mana_color
                                            for mana_color, ratio in mana_symbol_ratios.items()
                                            if ratio >= 0.05}
    splash_mana_colors = set(mana_symbol_ratios.keys()) - dominant_mana_colors
    deck_color_penalty = max(2 - len(dominant_mana_colors), 2) + len(splash_mana_colors)

    # Evaluate card archetypes
    archetype_penalty = 0
    if archetype_counts[Archetype.BOMB] == 0:
        archetype_penalty += 10
    if archetype_counts[Archetype.REMOVAL] < 2:
        distance_from_ideal = 2 - archetype_counts[Archetype.REMOVAL]
        archetype_penalty += 10 * distance_from_ideal

    deck_color_identity = dominant_mana_colors.union(splash_mana_colors)
    # TODO: Check if at least one of the colors is known for having flying

    if archetype_counts[Archetype.EVASIVE] < 2:
        distance_from_ideal = 2 - archetype_counts[Archetype.EVASIVE]
        archetype_penalty += 10 * distance_from_ideal

    archetype_penalty += duds_count * 5

    if len(deck_color_identity) > 1 and archetype_counts[Archetype.MANA_FIXING] < 2:
        distance_from_ideal = 2 - archetype_counts[Archetype.MANA_FIXING]
        archetype_penalty += 10 * distance_from_ideal

    # Combine objectives
    total_penalty = number_of_cards_penalty + land_ratio_penalty + \
        mana_symbol_ratio_penalty + deck_color_penalty + archetype_penalty

    return total_penalty


if __name__ == '__main__':
    import argparse
    import csv

    parser = argparse.ArgumentParser(description='Compute an optimal deck given a set of booster packs')
    parser.add_argument('ratings-file', metavar='RATING', type=argparse.FileType('r'),
                        help='The ratings list as a CSV')

    cards: Dict[CardId, Card] = {}
    card_types = CardTypes(lands={}, enchantments={}, artifacts={}, planeswalkers={}, creatures={}, sorceries={},
                           instants={})

    args = parser.parse_args()
    with args.ratings_file as ratings_file:
        ratings: Iterator[List[str]] = csv.reader(ratings_file)
        _ = next(ratings)  # Skip header row
        for rating in ratings:
            card_id, card_name, mana_cost, cmc, card_type, rarity, guild, \
                bomb, removal, combat_trick, evasive, counter, card_draw, mana_fixing, card_set, image_url = rating
            rarity = Rarity(rarity)
            card = Card(name=card_name, mana_cost=mana_cost, converted_mana_cost=cmc, type_info=card_type)
            cards[card_id] = card
