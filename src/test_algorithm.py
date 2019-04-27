#!/usr/bin/env python3

from collections import defaultdict
from typing import *

from hypothesis import given
from hypothesis.strategies import *
from yaml import safe_load

from algorithm import Deck, CardId, generate_booster_pack, summarize_deck, evaluate_deck


# Describe test case schema
class TestCard(NamedTuple):
    set: str
    card_number: int
    quantity: int = 1


class TestCase(NamedTuple):
    cards: Sequence[TestCard]


# Document root
class TestFileSchema(NamedTuple):
    cases: Sequence[TestCase]


@given(lists(text(), min_size=40))
def test_generate_booster_packs(mtg_set):
    deck = generate_booster_pack(mtg_set)
    deck = tuple(deck)
    assert len(deck) >= 40


def test_evaluate_deck():
    for test_number, test_deck in enumerate(load_test_cases(), start=1):
        print(f'Evaluating test deck {test_number}')
        # TODO: Pass set_infos
        deck_summary = summarize_deck(test_deck)
        print(f'Deck summary: {deck_summary}')
        penalty = evaluate_deck(deck_summary)
        print(f'Penalty: {penalty}')
        print()


# noinspection PyArgumentList
def load_test_cases() -> Iterator[Deck]:
    # Read in test cases
    with open('test_algorithm_cases.yml') as file:
        file = safe_load(file)
        file = TestFileSchema(**file)
        for test_case in file.cases:
            test_case = TestCase(**test_case)

            deck: DefaultDict[CardId] = defaultdict(int)
            for card in test_case.cards:
                card = TestCard(**card)
                deck[card.set, card.card_number] += card.quantity

            yield deck


if __name__ == '__main__':
    import pytest

    pytest.main()
