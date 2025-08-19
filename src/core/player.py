# ==============================================================================
# src/core/player.py
# NEUE DATEI in diesem Sprint.
# ==============================================================================
from typing import List
from src.core.deck import Deck
from src.core.cards import ActionCard

class Player:
    """Represents a player in the game, holding a hand of cards."""
    def __init__(self, name: str):
        self.name = name
        self.hand: List[ActionCard] = []

    def draw_hand(self, deck: Deck, num_cards: int = 4):
        """Draws cards from the deck to fill the player's hand up to num_cards."""
        while len(self.hand) < num_cards and not deck.is_empty():
            card = deck.draw()
            if card:
                self.hand.append(card)
        print(f"{self.name} drew a hand of {len(self.hand)} cards.")

    def __repr__(self):
        return f"Player({self.name}, Hand: {len(self.hand)} cards)"