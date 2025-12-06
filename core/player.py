"""
玩家基类
"""
from abc import ABC, abstractmethod
from .stone import Stone
from .position import Position


class Player(ABC):
    """玩家抽象基类"""
    
    def __init__(self, color: Stone, name: str, profile: dict = None):
        if color == Stone.EMPTY:
            raise ValueError("Player color cannot be EMPTY")
        self.color = color
        self.name = name
        self.profile = profile or {}
    
    @abstractmethod
    def make_move(self, game) -> Position:
        """玩家落子（子类实现）"""
        pass
    
    def __str__(self):
        return f"{self.name} ({self.color})"

