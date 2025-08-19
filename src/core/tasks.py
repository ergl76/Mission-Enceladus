# ==============================================================================
# src/core/tasks.py
# Datenstrukturen für alle Herausforderungen (Krisen und Pflichtaufgaben).
# ==============================================================================
from typing import Dict, List, Any

"""
Defines the data structures for tasks that players must overcome,
like crises and duties.
"""

class Task:
    """Base class for any challenge with symbol requirements."""
    def __init__(self, name: str, requirements: Dict[str, int]):
        self.name = name
        self.requirements = requirements # e.g. {constants.REPAIR: 2}

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, req: {self.requirements})"

class CrisisCard(Task):
    """
    Represents a crisis event. Requirements scale with player count.
    """
    def __init__(self, name: str, description: str, reward: str, penalty: str,
                 req_1_2_players: Dict[str, int],
                 req_3_4_players: Dict[str, int],
                 player_count: int = 2): # Defaulting to 2 for prototype
        
        # Select requirements based on player count
        if player_count <= 2:
            requirements = req_1_2_players
        else:
            requirements = req_3_4_players
            
        super().__init__(name, requirements)
        self.description = description
        self.reward = reward
        self.penalty = penalty

class DutyTask(Task):
    """
    Represents a recurring duty task for a specific game phase.
    """
    def __init__(self, name: str, penalty_escalation: List[str],
                 req_1_2_players: Dict[str, int],
                 req_3_4_players: Dict[str, int],
                 player_count: int = 2): # Defaulting to 2 for prototype

        # Select requirements based on player count
        if player_count <= 2:
            requirements = req_1_2_players
        else:
            requirements = req_3_4_players

        super().__init__(name, requirements)
        self.penalty_escalation = penalty_escalation