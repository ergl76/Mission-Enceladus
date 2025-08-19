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

    # Per specification: 8x Standard, 2x Efficiency, 1x Joker, 1x Support
    # 2 of each symbol for Standard cards
    cards.append(StandardCard("Nav-Computer Check", constants.NAVIGATION))
    cards.append(StandardCard("Recalibrate Sensors", constants.NAVIGATION))
    cards.append(StandardCard("Seal Micro-Fissure", constants.REPAIR))
    cards.append(StandardCard("Fix Actuator", constants.REPAIR))
    cards.append(StandardCard("Run Experiment", constants.RESEARCH))
    cards.append(StandardCard("Analyze Data", constants.RESEARCH))
    cards.append(StandardCard("Check CO2-Scrubber", constants.LIFE_SUPPORT))
    cards.append(StandardCard("Recycle Water", constants.LIFE_SUPPORT))

    # 2 Efficiency cards
    cards.append(EfficiencyCard("Optimized Repair", constants.REPAIR))
    cards.append(EfficiencyCard("Efficient Research", constants.RESEARCH))

    # 1 Joker and 1 Support card
    cards.append(JokerCard("All-Purpose Tool"))
    cards.append(SupportCard("Team Coordination"))

    action_deck = Deck(cards)
    action_deck.shuffle()
    return action_deck

def create_crisis_deck_phase1(player_count: int = 2) -> Deck:
    """Creates and populates the crisis deck for the first phase of the game."""
    crises = []

    # Crisis 1 from specification
    crises.append(CrisisCard(
        name="Unerwartete Sonneneruption",
        description="Ein koronaler Massenauswurf bedroht die Schiffselektronik!",
        reward="Schiffsintegrität +1, Rakete rückt 1 Feld vor.",
        penalty="Schiffsintegrität -1.",
        req_1_2_players={constants.REPAIR: 2},
        req_3_4_players={constants.REPAIR: 3, constants.NAVIGATION: 1},
        player_count=player_count
    ))

    # Crisis 2 from specification
    crises.append(CrisisCard(
        name="Klemmendes Treibstoffventil",
        description="Ein wichtiges Ventil für den nächsten Schub klemmt.",
        reward="Treibstoff +1, Rakete rückt 1 Feld vor.",
        penalty="Treibstoff -1.",
        req_1_2_players={constants.REPAIR: 1, constants.NAVIGATION: 1},
        req_3_4_players={constants.REPAIR: 2, constants.NAVIGATION: 1},
        player_count=player_count
    ))

    # Crisis 3 (additional)
    crises.append(CrisisCard(
        name="Falsche Sensordaten",
        description="Die Navigationssensoren liefern widersprüchliche Daten.",
        reward="Rakete rückt 2 Felder vor.",
        penalty="Rakete rückt nicht vor.",
        req_1_2_players={constants.RESEARCH: 1, constants.NAVIGATION: 1},
        req_3_4_players={constants.RESEARCH: 2, constants.NAVIGATION: 2},
        player_count=player_count
    ))

    # Crisis 4 (additional)
    crises.append(CrisisCard(
        name="Alarm im Lebenserhaltungssystem",
        description="Ein Sensor meldet einen kritischen Abfall der Luftqualität.",
        reward="Sauerstoff +1.",
        penalty="Sauerstoff -2.",
        req_1_2_players={constants.LIFE_SUPPORT: 2},
        req_3_4_players={constants.LIFE_SUPPORT: 3},
        player_count=player_count
    ))

    # Crisis 5 (additional)
    crises.append(CrisisCard(
        name="Wissenschaftliches Rätsel",
        description="Eine unerwartete Gravitationsanomalie erfordert sofortige Analyse.",
        reward="Ziehe 2 zusätzliche Aktionskarten.",
        penalty="Wirf 2 Handkarten ab.",
        req_1_2_players={constants.RESEARCH: 2},
        req_3_4_players={constants.RESEARCH: 3},
        player_count=player_count
    ))

    crisis_deck = Deck(crises)
    # Crisis decks are typically not shuffled at the start, but we can do it.
    crisis_deck.shuffle() 
    return crisis_deck