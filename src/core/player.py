# ==============================================================================
# src/core/player.py
# Hinzugefügt: 'is_ready' Attribut für das Ready-Check-System.
# ==============================================================================
from typing import List
from src.core.deck import Deck
from src.core.cards import ActionCard

class Player:
    """Represents a player in the game, holding a hand of cards."""
    def __init__(self, name: str):
        self.name = name
        self.hand: List[ActionCard] = []
        self.is_ready: bool = False # Neu für Ready-Check-System

    def draw_hand(self, deck: Deck, num_cards: int = 4):
        """Draws cards from the deck to fill the player's hand up to num_cards."""
        drew_cards = 0
        while len(self.hand) < num_cards and not deck.is_empty():
            card = deck.draw()
            if card:
                self.hand.append(card)
                drew_cards += 1
        if drew_cards > 0:
            print(f"{self.name} drew {drew_cards} card(s). Hand size: {len(self.hand)}.")

    def __repr__(self):
        return f"Player({self.name}, Hand: {len(self.hand)} cards)"