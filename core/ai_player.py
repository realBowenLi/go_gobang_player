"""
AI 玩家集合
"""
import random
from typing import Optional, List
from .player import Player
from .stone import Stone
from .position import Position


class AIPlayer(Player):
    """AI 基类，便于扩展不同等级的策略"""

    def __init__(self, color: Stone, name: str, level: int, profile: dict = None):
        super().__init__(color, name, profile=profile)
        self.level = level

    def __str__(self):
        return f"{self.name}(Lv{self.level})"


class RandomAI(AIPlayer):
    """一级 AI：完全随机选择合法位置"""

    def __init__(self, color: Stone, name: str = "AI", profile: dict = None):
        super().__init__(color, name, level=1, profile=profile)

    def make_move(self, game) -> Position:
        board = game.board
        size = board.size
        candidates: List[Position] = []
        for row in range(size):
            for col in range(size):
                pos = Position(row, col)
                # 对围棋虚着逻辑不做随机处理，只选择合法落子
                if board.is_empty(pos) and board.is_valid_move(pos, self.color):
                    candidates.append(pos)
        if not candidates:
            raise ValueError("No valid moves available")
        return random.choice(candidates)


class SuperAI(AIPlayer):
    """二级 AI：优先选择与对手上一手相邻的位置，否则随机"""

    def __init__(self, color: Stone, name: str = "超级AI", profile: dict = None):
        super().__init__(color, name, level=2, profile=profile)
        self.last_opponent_move: Optional[Position] = None

    def make_move(self, game) -> Position:
        board = game.board
        size = board.size

        if self.last_opponent_move:
            adjacent_positions = self.last_opponent_move.get_adjacent_positions(size)
            valid_adjacent = [
                pos for pos in adjacent_positions
                if board.is_empty(pos) and board.is_valid_move(pos, self.color)
            ]
            if valid_adjacent:
                return random.choice(valid_adjacent)

        return self._random_move(board, size)

    def _random_move(self, board, size: int) -> Position:
        empty_positions = []
        for row in range(size):
            for col in range(size):
                pos = Position(row, col)
                if board.is_empty(pos) and board.is_valid_move(pos, self.color):
                    empty_positions.append(pos)

        if not empty_positions:
            raise ValueError("No valid moves available")

        return random.choice(empty_positions)

    def update_opponent_move(self, position: Position):
        """更新对手的落子位置"""
        self.last_opponent_move = position

    def reset(self):
        """重置AI状态"""
        self.last_opponent_move = None

