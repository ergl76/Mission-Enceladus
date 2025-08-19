# ==============================================================================
# src/game/decks.py
# Funktionen zur Erstellung der initialen Kartenstapel des Spiels.
# ==============================================================================
from src.core import constants
from src.core.cards import StandardCard, EfficiencyCard, JokerCard, SupportCard
from src.core.tasks import CrisisCard
from src.core.deck import Deck

"""
Factory functions to create and initialize all necessary card decks for the game start.
"""

def create_initial_action_deck() -> Deck:
    """Creates, populates, and shuffles the main action deck."""
    cards = []
    
    # Per Bugfix-Auftrag: Erhöhung auf 32 Karten.
    
    # 20x StandardCard (5 pro Symbol)
    symbols = [constants.NAVIGATION, constants.REPAIR, constants.RESEARCH, constants.LIFE_SUPPORT]
    for symbol in symbols:
        for i in range(5):
            cards.append(StandardCard(f"{symbol[:4]}-Routine {i+1}", symbol))
            
    # 8x EfficiencyCard (2 pro Symbol)
    for symbol in symbols:
        for i in range(2):
            cards.append(EfficiencyCard(f"Effizienz-{symbol[:4]} {i+1}", symbol))

    # 2x JokerCard
    cards.append(JokerCard("Universal-Werkzeug"))
    cards.append(JokerCard("Reserve-Tool"))
    
    # 2x SupportCard
    cards.append(SupportCard("Team-Anweisung"))
    cards.append(SupportCard("Koordination"))
    
    action_deck = Deck(cards)
    action_deck.shuffle()
    return action_deck

def create_crisis_deck_phase1(player_count: int = 4) -> Deck:
    """Creates and populates the crisis deck for the first phase of the game."""
    crises = [
        CrisisCard(name="Unerwartete Sonneneruption", description="...", reward="...", penalty="...",
                   req_1_2_players={constants.REPAIR: 2}, req_3_4_players={constants.REPAIR: 3, constants.NAVIGATION: 1}, player_count=player_count),
        CrisisCard(name="Klemmendes Treibstoffventil", description="...", reward="...", penalty="...",
                   req_1_2_players={constants.REPAIR: 1, constants.NAVIGATION: 1}, req_3_4_players={constants.REPAIR: 2, constants.NAVIGATION: 1}, player_count=player_count),
        CrisisCard(name="Falsche Sensordaten", description="...", reward="...", penalty="...",
                   req_1_2_players={constants.RESEARCH: 1, constants.NAVIGATION: 1}, req_3_4_players={constants.RESEARCH: 2, constants.NAVIGATION: 2}, player_count=player_count),
    ]
    crisis_deck = Deck(crises)
    crisis_deck.shuffle()
    return crisis_deck