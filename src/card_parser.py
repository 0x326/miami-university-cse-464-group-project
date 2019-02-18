from mtgsdk import Card, Set, Type, Supertype, Subtype, Changelog

# cardList = Card.where(set = 'grn').where(language="English").all()
# print('cardList size: ' + str(cardList.__len__()))
# for card in cardList:
#     print(card.name)

booster = Set.generate_booster('grn')
for card in booster:
    print(f'{card.name} Rarity: {card.rarity}')
