# ==============================================================================
# src/core/player.py
# Bereinigt: Alle kartenbezogenen Attribute und Methoden wurden entfernt.
# ==============================================================================
class Player:
    """Represents a player with a specific specialization."""
    def __init__(self, name: str, specialization: str):
        self.name = name
        self.specialization = specialization
        self.is_ready: bool = False

    def __repr__(self):
        return f"Player({self.name}, Specialization: {self.specialization})"