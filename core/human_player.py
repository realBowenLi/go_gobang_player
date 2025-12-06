"""
人类玩家
"""
from .player import Player
from .stone import Stone
from .position import Position


class HumanPlayer(Player):
    """人类玩家"""

    def __init__(self, color: Stone, name: str = None, profile: dict = None):
        if name is None:
            name = "黑方" if color == Stone.BLACK else "白方"
        super().__init__(color, name, profile=profile)

    def make_move(self, game) -> Position:
        """人类玩家通过输入获取落子位置（实际由控制器处理）"""
        raise NotImplementedError("Human player moves are handled by the controller")
