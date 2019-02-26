from mtgsdk import Card, Set, Type, Supertype, Subtype, Changelog

# cardList = Card.where(set = 'grn').where(language="English").all()
# print('cardList size: ' + str(cardList.__len__()))
# for card in cardList:
#     print(card.name)
print(Set.find('grn').booster)

#booster = Set.generate_booster('grn')
#print(len(booster))

grn = Card.where(set = 'grn').where(language="English").all()

file_object = open("GuildsOfRavnica.txt","w")

for card in grn:

    if(card.name == "Plains"):
        break
    file_object.write(f'{card.name:^30} | {(card.mana_cost if (card.mana_cost is not None) else ""):^20} | {card.cmc:^5} | {card.type.replace("—", "-"):^40} | {card.rarity:^10} | \n')
    #print(f'{card.name} Rarity: {card.rarity}')

file_object.close()
