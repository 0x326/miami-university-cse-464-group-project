from typing import Sequence


CardId = str
Deck = Sequence[CardId]


def evaluate_deck(deck: Deck) -> float:
    """
    :return: A penalty value which should be minimized
    """
    number_of_cards_penalty = (40 - len(deck)) ** 2
    return number_of_cards_penalty
