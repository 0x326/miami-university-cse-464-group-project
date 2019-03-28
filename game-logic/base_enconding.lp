%%%% Input Predicates %%%%

% Card database data
% player(PlayerId).
% set(SetId).
% card(CardId, SetId, Rarity).
% card_mana_cost(CardId, ManaColor, ManaCount).
% card_mana_cost_variable(CardId, ManaColor, VariableName).
% card_rule_exception(CardId, RuleNumber).

% Card types
% land(CardId, Color).
% enchantment(CardId, TargetType).
% artifact(CardId).
% planeswalker(CardId, Loyalty).
% planeswalker_action(CardId, LoyaltyEffect).
% creature(CardId, Power, Toughness).
% creature_ability(CardId, Ability).  % Such as flying, etc.
% socery(CardId).
% instant(CardId).

% Card archetypes
% card_archetype(CardId, Archetype).

% starting_deck(PlayerId, CardId, Quantity).

%%%% Game fact predicates %%%%

% mana_color(Color).
% rarity(Rarity).
% ability(Ability).
% archetype(Archetype).
% permanent(CardId).

%%%% Time tracking predicates %%%%

% turn(TurnId, ActivePlayerId, PreviousTurnId).
% turn_phase(TurnId, TurnPhase).
% turn_phase_order(PreviousTurnPhase, NextTurnPhase).

%%%% Book keeping predicates (board state) %%%%

% life_count(TurnId, TurnPhase, PlayerId, LifeCount).

% card_instance(CardInstanceId, CardId, OwnerPlayerId).
% card_present(TurnId, TurnPhase, CardInstanceId).
% summoning_sickness(TurnId, TurnPhse, CardInstanceId).
% card_tapped(TurnId, TurnPhase, CardInstanceId).
% card_attacking(TurnId, TurnPhase, CardInstanceId).
% card_blocking(TurnId, TurnPhase, CardInstanceId).

%%%% Card pile predicates %%%%

% hand(TurnId, TurnPhase, PlayerId, CardInstanceId).
% deck(TurnId, TurnPhase, PlayerId, CardInstanceId).
% graveyard(TurnId, TurnPhase, PlayerId, CardInstanceId).

%%%% Player action predicates %%%%

% untap_card(TurnId, TurnPhase, PlayerId, CardInstanceId).
% draw(TurnId, TurnPhase, PlayerId, CardInstanceId).
% mulligan(TurnId, TurnPhase, PlayerId).
% play_card(TurnId, TurnPhase, PlayerId, CardInstanceId).
% tap_card(TurnId, TurnPhase, PlayerId, CardInstanceId).
% declare_attacker(TurnId, TurnPhase, PlayerId, TargetId, CardInstanceId).
% declare_blocker(TurnId, TurnPhase, PlayerId, CardInstanceId).
% discard_card(TurnId, TurnPhase, PlayerId, CardInstanceId).

%%%% Combat phase predicates %%%%
% combat_damage(TurnId, TurnPhase, CardInstanceId, Damage).
% card_dies(TurnId, TurnPhase, CardInstanceId).

#program base.

%%%% Game facts %%%%

% The mana colors are as follows:
mana_color(any; white; blue; black; red; green; colorless; snow).

% The card rarities are as follows:
rarity(black; gray; yellow; red; green).

% Creature abilities are as follows:
ability(flying; reach; haste; vigilance).

% There are five different archetypes we can identify:
archetype(bomb; removal; advantage; evasion; win).

% Everything except a Sorcery and an instant is a permanent
permanent(CardId) :-
    card(CardId, _, _),
    land(CardId).

permanent(CardId) :-
    card(CardId, _, _),
    enchantment(CardId).

permanent(CardId) :-
    card(CardId, _, _),
    artifact(CardId).

permanent(CardId) :-
    card(CardId, _, _),
    planeswalker(CardId).

permanent(CardId) :-
    card(CardId, _, _),
    creature(CardId).

-permanent(CardId) :-
    card(CardId, _, _),
    socery(CardId).

-permanent(CardId) :-
    card(CardId, _, _),
    instant(CardId).

%%%% Time tracking %%%%

% A turn has five phases (beginning, pre_combat, combat, post_combat, ending)
turn_phase(TurnId, beginning; pre_combat; combat; post_combat; ending) :-
    turn(TurnId, _).

% Give order to turn phases (but not a total order)
turn_phase_order(beginning, pre_combat).
turn_phase_order(pre_combat, combat).
turn_phase_order(combat, post_combat).
turn_phase_order(post_combat, ending).

%%%% Book keeping: Beginning of turn %%%%

% Every player's life count at the beginning of a turn is the same as it was at the end of the previous turn
% (Persistence property of life counts)
life_count(TurnId, beginning, PlayerId, LifeCount) :-
    turn(TurnId, _, PreviousTurnId),
    life_count(PreviousTurnId, ending, PlayerId, LifeCount).

% An untapped card from the end of the previous turn is untapped at the start of the next turn
% (Persistence property of untapped cards)
-card_tapped(TurnId, beginning, CardInstanceId) :-
    turn(TurnId, _, PreviousTurnId),
    turn_phase(TurnId, beginning),
    -card_tapped(PreviousTurnId, ending, CardInstanceId).

% A tapped card from the end of the previous turn is tapped at the start of the next turn,
% unless we have already derived it isn't
% (Persistence property of tapped cards)
card_tapped(TurnId, beginning, CardInstanceId) :-
    turn(TurnId, _, PreviousTurnId),
    turn_phase(TurnId, beginning),
    card_tapped(PreviousTurnId, ending, CardInstanceId),
    not -card_tapped(TurnId, beginning, CardInstanceId).

% Creatures recover from summoning sickness during the beginning phase of their owner's turn
-summoning_sickness(TurnId, beginning, CardInstanceId) :-
    card_present(TurnId, beginning, CardInstanceId),
    card_instance(CardInstanceId, CardId, OwnerPlayerId),
    creature(CardId, _, _),
    turn(TurnId, ActivePlayerId, _),
    ActivePlayerId = OwnerPlayerId.

%%%% Book keeping: Phase-to-phase %%%%

% Every player's life count is the same as the previous phase, unless derived to be otherwise
life_count(TurnId, NextTurnPhase, PlayerId, LifeCount) :-
    life_count(TurnId, PreviousTurnPhase, PlayerId, LifeCount),
    turn_phase_order(PreviousTurnPhase, NextTurnPhase),
    not life_count(TurnId, NextTurnPhase, PlayerId, _).

% Tapped cards from the previous phase are still tapped in the next phase
% TODO: Allow for exceptions
card_tapped(TurnId, NextTurnPhase, CardInstanceId) :-
    card_tapped(TurnId, PreviousTurnPhase, CardInstanceId),
    turn_phase_order(PreviousTurnPhase, NextTurnPhase).

% Untapped cards from the previous phase are still untapped in the next phase,
% unless derived otherwise
-card_tapped(TurnId, NextTurnPhase, CardInstanceId) :-
    -card_tapped(TurnId, PreviousTurnPhase, CardInstanceId),
    turn_phase_order(PreviousTurnPhase, NextTurnPhase),
    not card_tapped(TurnId, NextTurnPhase, CardInstanceId).

% Summoning sickness persists from the previous turn phase to the next
summoning_sickness(TurnId, NextTurnPhase, CardInstanceId) :-
    summoning_sickness(TurnId, PreviousTurnPhase, CardInstanceId),
    turn_phase_order(PreviousTurnPhase, NextTurnPhase).

% Cards on the board during the previous turn phase stay on the board during the next,
% unless derived otherwise
card_present(TurnId, NextTurnPhase, CardInstanceId) :-
    card_present(TurnId, PreviousTurnPhase, CardInstanceId),
    turn_phase_order(PreviousTurnPhase, NextTurnPhase),
    not -card_present(TurnId, NextTurnPhase, CardInstanceId).

% Cards off the board during the previous turn phase stay off the board during the next,
% unless derived otherwise
-card_present(TurnId, NextTurnPhase, CardInstanceId) :-
    -card_present(TurnId, PreviousTurnPhase, CardInstanceId),
    turn_phase_order(PreviousTurnPhase, NextTurnPhase),
    not card_present(TurnId, NextTurnPhase, CardInstanceId).

% Cards in a player's hand stay in his hand from phase to phase,
% unless derived otherwise
hand(TurnId, NextTurnPhase, PlayerId, CardInstanceId) :-
    hand(TurnId, PreviousTurnId, PlayerId, CardInstanceId),
    turn_phase_order(PreviousTurnPhase, NextTurnPhase),
    not -hand(TurnId, NextTurnPhase, PlayerId, CardInstanceId).

%%%% Book keeping: combat %%%%

% A blocking creature receives damage equal to the difference of
% his toughness to the attacker's power
combat_damage(TurnId, TurnPhase, CardInstanceId, Damage) :-
    declare_attacker(TurnId, TurnPhase, _, TargetId, AttackerCardInstanceId),
    declare_blocker(TurnId, TurnPhase, _, CardInstanceId),
    card_instance(AttackerCardInstanceId, AttackerCardId, _),
    card_instance(CardInstanceId, CardId, _),
    creature(AttackerCardId, Power, _),
    creature(CardId, _, Toughness),
    Damage = Toughness - Power.

% An attacking creature receives damage equal to the difference of
% his toughness to the blocker's power
combat_damage(TurnId, TurnPhase, CardInstanceId, Damage) :-
    declare_attacker(TurnId, TurnPhase, _, TargetId, CardInstanceId),
    declare_blocker(TurnId, TurnPhase, _, BlockerCardInstanceId),
    card_instance(CardInstanceId, CardId, _),
    card_instance(BlockerCardInstanceId, BlockerCardId, _),
    creature(BlockerCardId, Power, _),
    creature(CardId, _, Toughness),
    Damage = Toughness - Power.

% A creature dies when its combat damage is at least its toughness
card_dies(TurnId, TurnPhase, CardInstanceId) :-
    combat_damage(TurnId, TurnPhase, CardInstanceId, Damage),
    card_instance(CardInstanceId, CardId, _),
    creature(CardId, _, Toughness),
    Damage >= Toughness.

% When a card dies, it leaves the board in the next turn phase
-card_present(TurnId, NextTurnPhase, CardInstanceId) :-
    card_dies(TurnId, PreviousTurnPhase, CardInstanceId),
    turn_phase_order(PreviousTurnPhase, NextTurnPhase).

% When a card dies, it enters the graveyard in the next turn phase
graveyard(TurnId, NextTurnPhase, OwnerPlayerId, CardInstanceId) :-
    card_dies(TurnId, PreviousTurnPhase, CardInstanceId),
    card_instance(CardInstanceId, _, OwnerPlayerId),
    turn_phase_order(PreviousTurnPhase, NextTurnPhase).

%%%% Player action %%%%

% Players' "draw" action adds the card to their hand
hand(TurnId, TurnPhase, PlayerId, CardInstanceId) :-
    draw(TurnId, TurnPhase, PlayerId, CardInstanceId).

% Players' "draw" action removes the card from their deck
-deck(TurnId, TurnPhase, PlayerId, CardInstanceId) :-
    draw(TurnId, TurnPhase, PlayerId, CardInstanceId).

% Players' "play_card" action removes the card from their hand
-hand(TurnId, TurnPhase, PlayerId, CardInstanceId) :-
    play_card(TurnId, TurnPhase, PlayerId, CardInstanceId).

% Players' "play_card" action adds the card to the board, if it is a permanent
card_present(TurnId, TurnPhase, CardInstanceId) :-
    card_instance(CardInstanceId, CardId, _),
    permanent(CardId),
    play_card(TurnId, TurnPhase, _, CardInstanceId).

% Players' "tap" action taps the card
card_tapped(TurnId, TurnPhase, CardInstanceId) :-
    tap_card(TurnId, TurnPhase, _, CardInstanceId).

% Players' "untap" action untaps the card
-card_tapped(TurnId, TurnPhase, CardInstanceId) :-
    untap_card(TurnId, TurnPhase, _, CardInstanceId).

% Players' "discard_card" action removes the card from his hand
-hand(TurnId, TurnPhase, CardInstanceId) :-
    discard_card(TurnId, TurnPhase, CardInstanceId).

% Players' "discard_card" action adds the card to his graveyard
graveyard(TurnId, TurnPhase, PlayerId, CardInstanceId) :-
    discard_card(TurnId, TurnPhase, PlayerId, CardInstanceId).



% Every player untaps all of his cards at the beginning of his turn
% TODO: Make sure this rule only untaps tapable cards (such as lands and creatures)
untap_card(TurnId, beginning, PlayerId, CardInstanceId) :-
    turn_phase(TurnId, beginning),
    turn(TurnId, ActivePlayerId, _),
    card_present(TurnId, beginning, CardInstanceId),
    card_instance(CardInstanceId, OwnerPlayerId)
    ActivePlayerId = OwnerPlayerId,
    PlayerId = ActivePlayerId.

%%%% Integrity constraints %%%%

% A card cannot be in both a player's hand and deck at the same time
:-
    hand(TurnId, TurnPhase, _, CardInstanceId),
    deck(TurnId, TurnPhase, _, CardInstanceId).

% A card cannot be in both a player's hand and graveyard at the same time
:-
    hand(TurnId, TurnPhase, _, CardInstanceId),
    graveyard(TurnId, TurnPhase, _, CardInstanceId).

% A card cannot be in both a player's deck and graveyard at the same time
:-
    deck(TurnId, TurnPhase, _, CardInstanceId),
    graveyard(TurnId, TurnPhase, _, CardInstanceId).
