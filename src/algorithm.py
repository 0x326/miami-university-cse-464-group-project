#!/usr/bin/env python3

"""
Magic: The Gathering Tournament Deck Optimizer
"""

import operator
import random
from collections import Counter, defaultdict
from enum import Enum, auto, unique
from itertools import accumulate, chain
from typing import *
from urllib.parse import ParseResult, urlparse

K = TypeVar('K')
V = TypeVar('V')


def zip_dict(*dictionaries: Mapping[K, V]) -> Iterator[Tuple[K, Iterator[V]]]:
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

# We will represent the "set" containing basic lands as None
SetId = Optional[str]
CardNumber = int
CardFaceId = Tuple[CardNumber, Index]
CardId = Tuple[SetId, CardNumber]
Deck = Mapping[CardId, Count]


@unique
class ManaColor(Enum):
    ANY = auto()
    WHITE = 'W'
    BLUE = 'U'
    BLACK = 'B'
    RED = 'R'
    GREEN = 'G'
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
    LAND = 'Land'
    ENCHANTMENT = 'Enchantment'
    ARTIFACT = 'Artifact'
    PLANESWALKER = 'Planeswalker'
    CREATURE = 'Creature'
    SORCERY = 'Sorcery'


@unique
class Guild(Enum):
    AZORIUS = auto()
    DIMIR = auto()
    RAKDOS = auto()
    GRUUL = auto()
    SELESNYA = auto()
    ORZHOV = auto()
    IZZET = auto()
    GOLGARI = auto()
    BOROS = auto()
    SIMIC = auto()


class Land(NamedTuple):
    possible_colors: AbstractSet[ManaColor]


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
    # The "Any" mana cost should be represented as {ManaColor.ANY} instead of {ManaColor.WHITE, ManaColor.BLUE, ...}
    mana_cost: Mapping[AbstractSet[ManaColor], Count]
    converted_mana_cost: int
    type: CardType


class Card(NamedTuple):
    faces: Sequence[CardFace]
    rarity: Rarity
    rating: int
    guild: Optional[Guild]
    image_url: Optional[ParseResult]
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
    set_name: str
    cards: Mapping[CardNumber, Card]
    card_types: CardTypes
    rarities: Mapping[Rarity, AbstractSet[CardNumber]]
    ratings: Mapping[int, AbstractSet[CardNumber]]
    guilds: Mapping[Guild, AbstractSet[CardNumber]]
    archetypes: Mapping[Archetype, AbstractSet[CardNumber]]


class DeckSummary(NamedTuple):
    total_cards: int
    converted_mana_cost_cdf: Iterator[float]
    total_land_ratio: float
    mana_symbol_pmf: Mapping[ManaColor, float]
    land_color_pmf: Mapping[ManaColor, float]
    color_identity: AbstractSet[ManaColor]
    dominant_mana_colors: AbstractSet[ManaColor]
    splash_mana_colors: AbstractSet[ManaColor]
    archetype_counts: Mapping[Archetype, int]
    dud_count: int


def generate_booster_pack(set_info: SetInfo) -> Iterator[CardNumber]:
    """
    Generates a booster pack from the given Magic: The Gathering "set" (repetition of cards is allowed)

    :param set_info: The "set" to choose the cards from
    :return: The booster pack
    """
    # Typical Booster pack layout: 10 Commons, 3 Uncommons, 1 Rare or Mythic (roughly 1/7 chance to get a mythic)
    # Foils replace a card in the common slot (no matter the rarity of the foil) and also have roughly 1/7 chance
    # always includes 1 land (guildgate in this case)

    # Foil & Commons
    if random.randrange(7) == 0:
        # 1 Foil & 9 Commons
        yield from random.choice(set_info.cards.keys())
        yield from random.sample(set_info.rarities[Rarity.COMMON], k=9)
    else:
        # 10 Commons
        yield from random.sample(set_info.rarities[Rarity.COMMON], k=10)

    # Uncommons
    yield from random.choices(set_info.rarities[Rarity.UNCOMMON], k=3)

    # Rare/Mythic Rare
    rares = set_info.rarities[Rarity.RARE]
    rare_weights = (7,) * len(rares)
    mythic_rares = set_info.rarities[Rarity.MYTHIC_RARE]
    mythic_rare_weights = (1,) * len(mythic_rares)
    yield from random.choices(chain(rares, mythic_rares), cum_weights=chain(rare_weights, mythic_rare_weights))


def summarize_deck(deck: Deck, set_infos: Mapping[SetId, SetInfo]) -> DeckSummary:
    """
    Consolidates the deck into quantitative attributes so that it can be evaluated

    :param deck: The deck to summarize
    :param set_infos: Information about the set of which this deck is drawn
    :return: A summary of the deck's attributes
    """
    # Definitions:
    # CDF: Cumulative distribution function
    # PMF: Probability mass function

    # Deck counts
    total_cards: int = 0
    land_counts: DefaultDict[ManaColor, float] = defaultdict(float)
    mana_symbol_counts: DefaultDict[ManaColor, float] = defaultdict(float)
    converted_mana_cost_counts: List[int] = [0] * 6
    archetype_counts: DefaultDict[Archetype, int] = defaultdict(int)
    dud_count: int = 0

    for (set_id, card_number), card_quantity in deck.items():
        cards = set_infos[set_id].cards
        lands = set_infos[set_id].card_types.lands

        card = cards[card_id]

        # Total cards
        total_cards += card_quantity

        # Lands
        for face_index, _ in enumerate(card.faces):
            try:
                mana_colors = lands[card_id, face_index].possible_colors
            except KeyError:
                pass
            else:
                for mana_color in mana_colors:
                    # In the case of a dual land, count 0.5 for each color
                    land_counts[mana_color] += card_quantity / len(mana_colors)
                break  # Only count one land per card

        # Mana symbols
        for face in card.faces:
            for mana_colors, mana_quantity in face.mana_cost.items():
                for mana_color in mana_colors:
                    # In the case of a split mana symbol, count 0.5 for each half
                    mana_symbol_counts[mana_color] += mana_quantity * card_quantity / len(mana_colors)

        # Converted mana cost
        for face in card.faces:
            try:
                # Leaves index 0 unoccupied - Allowed for code elegance
                converted_mana_cost_counts[face.converted_mana_cost] += card_quantity
            except IndexError:
                # For the purposes of deck evaluation, we are only considering the converted mana cost <= 5
                pass

        # Archetypes
        for archetype in card.archetypes:
            archetype_counts[archetype] += card_quantity

        # Duds
        if card.rating <= 1:
            dud_count += card_quantity

    # Summarize mana curve
    total_converted_mana_cost_count = sum(converted_mana_cost_counts)
    converted_mana_cost_pmf: Iterator[float] = (count / total_converted_mana_cost_count
                                                for count in converted_mana_cost_counts)
    converted_mana_cost_cdf = accumulate(converted_mana_cost_pmf, operator.add)

    # Summarize land percentage
    total_land_count = sum(land_counts.values())
    total_land_ratio = total_land_count / total_cards

    # Summarize land color percentage
    total_mana_symbol_count = sum(mana_symbol_counts.values())
    mana_symbol_pmf: Dict[ManaColor, float] = {color: count / total_mana_symbol_count
                                               for color, count in mana_symbol_counts.items()}

    land_color_pmf: Dict[ManaColor, float] = {color: count / total_land_count
                                              for color, count in land_counts.items()}

    # Summarize color identity
    deck_color_identity = set(mana_symbol_pmf.keys())
    dominant_mana_colors: Set[ManaColor] = {mana_color
                                            for mana_color, probability_mass in mana_symbol_pmf.items()
                                            if probability_mass >= 0.05}
    splash_mana_colors = deck_color_identity - dominant_mana_colors

    return DeckSummary(total_cards=total_cards,
                       converted_mana_cost_cdf=converted_mana_cost_cdf,
                       total_land_ratio=total_land_ratio,
                       mana_symbol_pmf=mana_symbol_pmf, land_color_pmf=land_color_pmf,
                       color_identity=deck_color_identity,
                       dominant_mana_colors=dominant_mana_colors, splash_mana_colors=splash_mana_colors,
                       archetype_counts=archetype_counts, dud_count=dud_count)


def evaluate_deck(deck: DeckSummary) -> float:
    """
    Evaluates a deck against a predetermined ideal and penalizes it accordingly.

    :param deck: The deck to evaluate
    :return: A penalty value which should be minimized
    """
    # Evaluate deck size
    number_of_cards_penalty = (40 - deck.total_cards) ** 2

    # Evaluate mana curve
    expected_cmc_cdf = (
        0.05,
        0.31,
        0.52,
        0.73,
        0.89)

    mana_curve_penalty = sum(abs(expected_cdf_value - actual_cdf_value)
                             for expected_cdf_value, actual_cdf_value
                             in zip(expected_cmc_cdf, deck.converted_mana_cost_cdf))

    # Evaluate land percentage
    land_ratio_penalty = 0 if 16 / 40 <= deck.total_land_ratio <= 18 / 40 else abs(17 / 40 - deck.total_land_ratio)

    # Evaluate land color percentage
    mana_symbol_penalty: float = sum(abs(mana_symbol_probability_mass - land_probability_mass)
                                     for _, (mana_symbol_probability_mass, land_probability_mass)
                                     in zip_dict(deck.mana_symbol_pmf, deck.land_color_pmf))

    # Evaluate color identity
    deck_color_penalty = max(2 - len(deck.dominant_mana_colors), 2) + len(deck.splash_mana_colors)

    # Evaluate card archetypes
    archetype_penalty = 0

    bombs = deck.archetype_counts[Archetype.BOMB]
    removals = deck.archetype_counts[Archetype.REMOVAL]
    evasive_count = deck.archetype_counts[Archetype.EVASIVE]
    mana_fixing_count = deck.archetype_counts[Archetype.MANA_FIXING]

    if bombs == 0:
        archetype_penalty += 10
    if removals < 2:
        distance_from_ideal = 2 - removals
        archetype_penalty += 10 * distance_from_ideal

    # TODO: Check if at least one of the colors is known for having flying

    if evasive_count < 2:
        distance_from_ideal = 2 - evasive_count
        archetype_penalty += 10 * distance_from_ideal

    archetype_penalty += deck.dud_count * 5

    if len(deck.color_identity) > 1 and mana_fixing_count < 2:
        distance_from_ideal = 2 - mana_fixing_count
        archetype_penalty += 10 * distance_from_ideal

    # Combine objectives
    total_penalty = number_of_cards_penalty + mana_curve_penalty + land_ratio_penalty + \
        mana_symbol_penalty + deck_color_penalty + archetype_penalty

    return total_penalty


if __name__ == '__main__':
    import argparse
    import csv

    parser = argparse.ArgumentParser(description='Compute an optimal deck given a set of booster packs')
    parser.add_argument('ratings', metavar='RATING', type=argparse.FileType('r'),
                        help='The ratings list as a CSV')

    # Pre-define basic lands
    basic_lands = (('Plains', ManaColor.WHITE),
                   ('Island', ManaColor.BLUE),
                   ('Swamp', ManaColor.BLACK),
                   ('Mountain', ManaColor.RED),
                   ('Forest', ManaColor.GREEN))
    basic_land_rarity = Rarity.COMMON
    basic_land_rating = 1
    basic_land_card_numbers = frozenset(card_number for card_number, _ in enumerate(basic_lands, start=1))

    empty_set = frozenset()

    set_infos: Dict[SetId, SetInfo] = {
        None: SetInfo(set_name='Basic lands',
                      cards={card_number: Card(
                          faces=(
                              CardFace(name=card_name, mana_cost={}, converted_mana_cost=0,
                                       type=CardType.LAND),
                          ),
                          rarity=basic_land_rarity,
                          rating=basic_land_rating,
                          guild=None,
                          image_url=None,
                          archetypes=empty_set)
                          for card_number, (card_name, _) in enumerate(basic_lands, start=1)
                      },
                      card_types=CardTypes(
                          lands={(card_number, 0): Land(frozenset({mana_color}))
                                 for card_number, (_, mana_color) in enumerate(basic_lands, start=1)},
                          enchantments={},
                          artifacts={},
                          planeswalkers={},
                          creatures={},
                          sorceries={},
                          instants={},
                      ),
                      rarities={basic_land_rarity: basic_land_card_numbers},
                      ratings={basic_land_rating: basic_land_card_numbers},
                      guilds={},
                      archetypes={})
    }

    cards: Dict[CardNumber, Card] = {}
    card_types = CardTypes(lands={}, enchantments={}, artifacts={}, planeswalkers={}, creatures={}, sorceries={},
                           instants={})

    args = parser.parse_args()
    with args.ratings as ratings_file:
        ratings: Iterator[List[str]] = csv.reader(ratings_file)
        _ = next(ratings)  # Skip header row
        for rating in ratings:
            card_set, card_number, card_name, mana_cost, cmc, card_type, rarity, rating_score,\
            guild, bomb, removal, combat_trick, evasive, counter, card_draw, mana_fixing, image_url = rating  # type: str

            card_number = int(card_number)

            mana_cost_text: str = mana_cost.upper()
            mana_cost_text = mana_cost_text.strip('{}')
            mana_cost: DefaultDict[Set[ManaColor], Count] = defaultdict(int)
            for mana_cost_symbol in mana_cost_text.split('}{'):
                try:
                    mana_cost_symbol = int(mana_cost_symbol)

                except ValueError:
                    mana_quantity = 1
                    try:
                        left_mana_symbol, right_mana_symbol = mana_cost_symbol.split('/')

                    except ValueError:
                        # Single-color mana
                        mana_colors = {ManaColor(mana_cost_symbol)}

                    else:
                        # Split mana
                        mana_colors = {left_mana_symbol, right_mana_symbol}

                else:
                    # Any mana
                    mana_colors = {ManaColor.ANY}
                    mana_quantity = mana_cost_symbol

                mana_cost[mana_colors] += mana_quantity

            cmc = int(cmc)

            try:
                card_type_split = card_type.split(' ')
            except ValueError:
                # Single word in card_type
                card_kind = CardType(card_type)
            else:
                # Multiple words in card_type
                card_kind = CardType(card_type_split[0])


            # NULL is None in python
            # if guild.upper() == 'NULL'

            rarity = Rarity(rarity)

            try:
                num_card_rating = float(rating_score)
                # I don't really know what to put in the except and else but heres this
            except ValueError:
                pass
            else:
                pass

            guild = guild.upper()
            if guild == 'NULL':
                card_guild = None
            else:
                card_guild = Guild(guild)

            archetype_set: AbstractSet = AbstractSet

            # TODO: convert these booleans into the appropriate ENUMs

            bomb_bool = (bomb == '1')
            removal_bool = (removal == '1')
            combat_trick_bool = (combat_trick == '1')
            evasive_bool = (evasive == '1')
            counter_bool = (counter == '1')
            card_draw_bool = (card_draw == '1')
            mana_fixing_bool = (mana_fixing == '1')

            image_url: ParseResult = urlparse(image_url)

            faces = Sequence[CardFace]

            # TODO: Incorporate split cards
            try:
                left_card_name, right_card_name = card_name.split('//')

            except ValueError:
                # faces: Sequence[CardFace] = {}
                # put data into faces
                pass

            else:
                pass  # Continue on with split card

            # TODO: create the card object to be stored and store it
            # card = Card(name=card_name, mana_cost=mana_cost_text, converted_mana_cost=cmc, type_info=card_type)
            # cards[card_id] = card
