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
% card_bomb_archetype(CardId).
% card_removal_archetype(CardId).
% card_advantage_archetype(CardId).
% card_evasion_archetype(CardId).
% card_win_archetype(CardId).

% starting_deck(PlayerId, CardId, Quantity).

%%%% Time tracking predicates %%%%

% turn(TurnId).
% turn_phase(TurnId, TurnPhase).

%%%% Book keeping predicates (board state) %%%%

% life_count(TurnId, TurnPhase, PlayerId, LifeCount).

% card_present(TurnId, TurnPhase, CardInstanceId).
% summoning_sickness(TurnId, TurnPhse, CardInstanceId).
% card_tapped(TurnId, TurnPhase, CardInstanceId).
% card_attacking(TurnId, TurnPhase, CardInstanceId).
% card_blocking(TurnId, TurnPhase, CardInstanceId).

%%%% Card pile predicates %%%%

% deck(PlayerId, TurnId, TurnPhase, CardInstanceId, Quantity).
% graveyard(PlayerId, TurnId, TurnPhase, CardInstanceId, Quantity).

%%%% Player action predicates %%%%

% untap_card(TurnId, TurnPhase, PlayerId, CardInstanceId).
% draw(TurnId, TurnPhase, PlayerId, CardInstanceId).
% mulligan(TurnId, TurnPhase, PlayerId).
% play_card(TurnId, TurnPhase, PlayerId, CardInstanceId).
% tap_card(TurnId, TurnPhase, PlayerId, CardInstanceId).
% declare_attacker(TurnId, TurnPhase, PlayerId, TargetId, CardInstanceId).
% declare_blocker(TurnId, TurnPhase, PlayerId, CardInstanceId).
% discard_card(TurnId, TurnPhase, CardInstanceId).

%%%% Combat phase predicates %%%%
% combat_damage(TurnId, TurnPhase, CardInstanceId, Damage).
% card_dies(TurnId, TurnPhase, CardInstanceId).

#program base.

% mana_color(Color).
mana_color(any; white; blue; black; red; green; colorless; snow).

% rarity(Rarity).
rarity(black; gray; yellow; red; green).

% permanent(CardId).
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

turn_phase(TurnId, beginning; pre_combat; combat; post_combat; ending) :-
    turn(TurnId).
