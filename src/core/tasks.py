# ==============================================================================
# src/core/tasks.py
# REFACTORING: 'CrisisCard' wurde zu 'ChallengeCard' umbenannt.
# ==============================================================================
from typing import Dict, List

class Task:
    """Base class for any challenge with symbol requirements."""
    def __init__(self, name: str, requirements: Dict[str, int]):
        self.name = name
        self.requirements = requirements
    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, req: {self.requirements})"

class ChallengeCard(Task):
    """Represents a challenge event. Requirements scale with player count."""
    def __init__(self, name: str, description: str, reward: str, penalty: str,
                 req_1_2_players: Dict[str, int], req_3_4_players: Dict[str, int],
                 player_count: int = 4):
        requirements = req_1_2_players if player_count <= 2 else req_3_4_players
        super().__init__(name, requirements)
        self.description = description
        self.reward = reward
        self.penalty = penalty

class DutyTask(Task):
    """Represents a recurring duty task for a specific game phase."""
    def __init__(self, name: str, penalty_escalation: List[str],
                 req_1_2_players: Dict[str, int], req_3_4_players: Dict[str, int],
                 player_count: int = 4):
        requirements = req_1_2_players if player_count <= 2 else req_3_4_players
        super().__init__(name, requirements)
        self.penalty_escalation = penalty_escalation