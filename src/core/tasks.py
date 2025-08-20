# ==============================================================================
# src/core/tasks.py
# Umgebaut für das Energie-Management-System.
# ==============================================================================
class Task:
    """Base class for any challenge."""
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

class ChallengeCard(Task):
    """Represents a challenge event with thrust and navigation targets."""
    def __init__(self, name: str, description: str, reward: str, penalty: str,
                 target_thrust: int, target_navigation: int):
        super().__init__(name)
        self.description = description
        self.reward = reward
        self.penalty = penalty
        self.target_thrust = target_thrust
        self.target_navigation = target_navigation