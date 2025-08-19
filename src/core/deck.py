# ==============================================================================
# src/core/deck.py
# Eine generische Klasse zur Verwaltung von Kartenstapeln.
# ==============================================================================
import random
from typing import List, Union

# NEU: Importieren der Klassendefinitionen, die als Type-Hints verwendet werden.
from src.core.cards import ActionCard
from src.core.tasks import Task

"""
Provides a generic Deck class for managing collections of cards (or tasks).
"""

class Deck:
    """A generic deck of cards that can be shuffled, drawn from, etc."""
    # Die Typ-Definitionen ActionCard und Task sind jetzt bekannt.
    def __init__(self, cards: List[Union[ActionCard, Task]]):
        self.cards = list(cards)

    def shuffle(self):
        """Shuffles the cards in the deck randomly."""
        random.shuffle(self.cards)
        print("Deck has been shuffled.")

    def draw(self) -> Union[ActionCard, Task, None]:
        """Draws the top card from the deck. Returns None if empty."""
        if not self.is_empty():
            return self.cards.pop(0)
        return None

    def is_empty(self) -> bool:
        """Checks if the deck is empty."""
        return len(self.cards) == 0

    def __len__(self) -> int:
        return len(self.cards)

    def __repr__(self):
        return f"Deck({len(self.cards)} cards)"