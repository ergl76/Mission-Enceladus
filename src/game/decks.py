# ==============================================================================
# src/game/decks.py
# REFACTORING: Umbenennung von 'crisis' zu 'challenge'.
# ==============================================================================
from src.core import constants
from src.core.cards import StandardCard, EfficiencyCard, JokerCard, SupportCard
from src.core.tasks import ChallengeCard
from src.core.deck import Deck

def create_initial_action_deck() -> Deck:
    """Creates, populates, and shuffles the main action deck."""
    cards = []
    symbols = [constants.NAVIGATION, constants.REPAIR, constants.RESEARCH, constants.LIFE_SUPPORT]
    for symbol in symbols:
        for i in range(5):
            cards.append(StandardCard(f"{symbol[:4]}-Routine {i+1}", symbol))
    for symbol in symbols:
        for i in range(2):
            cards.append(EfficiencyCard(f"Effizienz-{symbol[:4]} {i+1}", symbol))
    cards.append(JokerCard("Universal-Werkzeug"))
    cards.append(JokerCard("Reserve-Tool"))
    cards.append(SupportCard("Team-Anweisung"))
    cards.append(SupportCard("Koordination"))
    
    action_deck = Deck(cards)
    action_deck.shuffle()
    return action_deck

def create_challenge_deck_phase1(player_count: int = 4) -> Deck:
    """Creates and populates the challenge deck for the first phase of the game."""
    challenges = [
        ChallengeCard(name="Unerwartete Sonneneruption", description="...", reward="Fortschritt", penalty="Integrität -1",
                   req_1_2_players={constants.REPAIR: 2}, req_3_4_players={constants.REPAIR: 3, constants.NAVIGATION: 1}, player_count=player_count),
        ChallengeCard(name="Klemmendes Treibstoffventil", description="...", reward="Fortschritt", penalty="Treibstoff -1",
                   req_1_2_players={constants.REPAIR: 1, constants.NAVIGATION: 1}, req_3_4_players={constants.REPAIR: 2, constants.NAVIGATION: 1}, player_count=player_count),
        ChallengeCard(name="Falsche Sensordaten", description="...", reward="Fortschritt", penalty="Nichts",
                   req_1_2_players={constants.RESEARCH: 1, constants.NAVIGATION: 1}, req_3_4_players={constants.RESEARCH: 2, constants.NAVIGATION: 2}, player_count=player_count),
    ]
    challenge_deck = Deck(challenges)
    challenge_deck.shuffle()
    return challenge_deck