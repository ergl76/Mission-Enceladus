# ==============================================================================
# src/core/cards.py
# Datenstrukturen für alle Typen von Aktionskarten im Spiel.
# ==============================================================================
import abc

"""
Defines the data structures for all action cards available to players.
Uses an abstract base class 'ActionCard' to establish a common interface.
"""

class ActionCard(abc.ABC):
    """Abstract base class for all action cards."""
    def __init__(self, name: str, card_type: str):
        self.name = name
        self.card_type = card_type

    def __repr__(self):
        return f"{self.card_type}({self.name})"

class StandardCard(ActionCard):
    """A standard action card that provides one specific symbol."""
    def __init__(self, name: str, symbol: str):
        super().__init__(name, "StandardCard")
        self.symbol = symbol

class EfficiencyCard(ActionCard):
    """
    An efficiency card that provides one specific symbol.
    Its special logic (counts as two symbols) will be implemented later.
    """
    def __init__(self, name: str, symbol: str):
        super().__init__(name, "EfficiencyCard")
        self.symbol = symbol

class JokerCard(ActionCard):
    """A flexible card that can be used as any symbol (logic to be implemented)."""
    def __init__(self, name: str = "Joker"):
        super().__init__(name, "JokerCard")

class SupportCard(ActionCard):
    """A special card with a unique supportive effect (logic to be implemented)."""
    def __init__(self, name: str = "Support"):
        super().__init__(name, "SupportCard")