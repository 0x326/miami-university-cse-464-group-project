#!/usr/bin/env python3

from hypothesis import given
from hypothesis.strategies import *

from algorithm import generate_booster_pack


@given(lists(text(), min_size=40))
def test_generate_booster_packs(mtg_set):
    deck = generate_booster_pack(mtg_set)
    deck = tuple(deck)
    assert len(deck) >= 40


if __name__ == '__main__':
    test_generate_booster_packs()
