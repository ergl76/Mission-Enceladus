# ==============================================================================
# src/game/decks.py
# Bereinigt: Aktionskarten-Logik entfernt.
# ==============================================================================
from src.core.tasks import ChallengeCard
from typing import List
import random

def create_challenge_deck_phase1(player_count: int = 4) -> List[ChallengeCard]:
    """Creates and populates the challenge deck for the first phase of the game."""
    challenges = [
        ChallengeCard(name="Asteroidenfeld durchqueren", description="...", reward="Fortschritt", penalty="Integrität -2",
                      target_thrust=4, target_navigation=6),
        ChallengeCard(name="Sonneneruption ausweichen", description="...", reward="Fortschritt", penalty="Systemschaden",
                      target_thrust=6, target_navigation=4),
        ChallengeCard(name="Orbitalkorrektur am Mars", description="...", reward="Fortschritt", penalty="Treibstoff -2",
                      target_thrust=5, target_navigation=5),
    ]
    random.shuffle(challenges)
    return challenges