#!/usr/bin/env python3

from mtgsdk import Card, Set, Type, Supertype, Subtype, Changelog

# cardList = Card.where(set = 'grn').where(language="English").all()
# print('cardList size: ' + str(cardList.__len__()))
# for card in cardList:
#     print(card.name)

# booster = Set.generate_booster('grn')
# print(len(booster))

grn = Card.where(set='rna').where(language="English").all()

with open("RavnicaAllegienceURLs.txt", "w") as file_object:

    for card in grn:

        if card.name == "Plains":
            break
        file_object.write(f'{card.image_url} \n')
