[clingo]: https://potassco.org/clingo/

# Game logic

## Prerequisites

- [clingo]: `scoop install clingo`

## Learning clingo

- [Online examples](https://potassco.org/clingo/run/)

## Magic the Gathering Gameplay Notes

- Goal: Reduce opponent's life count from 20 to 0
- Cards have:

  - Name
  - Mana cost:

    - Mana color (Any, White, Blue, Black, Red, Green, Colorless, Snow)
    - Quantity

  - Type line

    - Land (Color)
    - Enchantment

      - Enchant creature
      - Enchant land

    - Artifact
    - Planeswalker (Loyalty)

      - `+N` action
      - `-N` action
      - `-N` action

    - Creature (Power / Toughness)
    - Sorcery

      - (Can only be cast during your turn)

    - Instant

      - Added to the spell stack

  - Rarity

    - (Black)
    - (Gray)
    - (Yellow)
    - (Red)
    - (Green)

  - Text box

- Is there a restriction on how many of the same (non-land) card you're allowed to have?
- Tap cards; Tapped until next turn
- Creatures deal damage equal to their power
- Creatures have summoning sickness
- Everything except a Sorcery and an instant is a permanent
- Rules apply unless there is an exception
- Tapped creatures cannot block

- Turn phases:

  - Beginning phase

    - Untap step
    - Upkeep step (look for on-upkeep handlers; creatures recover from summoning sickness)
    - Draw step (Draw a card; You lose if you are out of cards)

  - Pre-combat main phase

    - Summon lands
    - Summon creatures, etc.
    - Enchant
    - Utilize planeswalkers

  - Combat phase

    - Beginning of combat step
    - Declare attackers step (at opponent or his planeswalker)
    - Declare blockers step
    - Combat damage step
    - End of combat step

  - Post-combat main phase

    - (It's smart to summon creatures after combat since they can't fight anyway
      and the opponent can't take them into consideration when choosing blockers)

  - Ending phase

    - End step
    - Clean-up step

      - Discard cards until hand is 7
      - Damage heals
