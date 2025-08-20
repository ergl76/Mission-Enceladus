# ==============================================================================
# src/game/decks.py
# Aktionskarten-Logik entfernt. Nur noch Erstellung des Herausforderungs-Decks.
# ==============================================================================
from src.core.tasks import ChallengeCard
from typing import List

def create_challenge_deck_phase1(player_count: int = 4) -> List[ChallengeCard]:
    """Creates and populates the challenge deck for the first phase of the game."""
    # Temporäre Deck-Implementierung als Liste, da die Deck-Klasse entfernt wurde.
    challenges = [
        ChallengeCard(name="Asteroidenfeld durchqueren", description="...", reward="Fortschritt", penalty="Integrität -2",
                      target_thrust=4, target_navigation=6),
        ChallengeCard(name="Sonneneruption ausweichen", description="...", reward="Fortschritt", penalty="Systemschaden",
                      target_thrust=6, target_navigation=4),
        ChallengeCard(name="Orbitalkorrektur am Mars", description="...", reward="Fortschritt", penalty="Treibstoff -2",
                      target_thrust=5, target_navigation=5),
    ]
    # In einer finalen Version würde hier Mischen etc. stattfinden.
    return challenges