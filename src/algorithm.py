from typing import Sequence


CardId = str
Deck = Sequence[CardId]


def evaluate_deck(deck: Deck) -> float:
    """
    :return: A penalty value which should be minimized
    """
    # OBJECTIVE 1
    number_of_cards_penalty = (40 - len(deck)) ** 2

    # OBJECTIVE 2
    '''
    '''

    # OBJECTIVE 3
    '''
    land_count = 0
    
    for card in deck:
        if card.type == "Land":
            land_count++
            
    land_ratio = land_count / len(deck)
    land_ratio_penalty = (abs(17/40 - land_ratio),0)[land_ratio >= 16/40 && land_ratio <= 18/40]
    '''

    # OBJECTIVE 3A
    '''
    mana_symbols = [0, 0, 0, 0, 0]
    total_mana_symbols = 0
    
    land_colors = [0, 0, 0, 0, 0]
    total_land_count = 0
    
    for card in deck:
        if card.type != "Land":
            total_land_count++
            // check what color mana land produces and increment correct value in land_colors
        else:
            for mana in card.ManaCost:
                try:
                    symbol = ["R", "B", "U", "G", "W"].index(mana)
                    total_mana_symbols++
                    mana_symbols[symbol]++
                except ValueError:
                    print("Howdy\n")
    
    mana_symbol_ratio_penalty = 0
    
    for i in range(4):
        mana_symbol_ratio_penalty += abs( (mana_symbols[i] / total_mana_symbols) - (land_colors[i] / total_land_count) )
    '''

    # OBJECTIVE 4
    '''
    '''

    # OBJECTIVE 5
    '''
    '''



    return number_of_cards_penalty
