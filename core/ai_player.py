"""
AI玩家（超级AI）
"""
import random
from typing import Optional
from .player import Player
from .stone import Stone
from .position import Position
from ..config import GameConfig


class SuperAI(Player):
    """超级AI玩家"""
    
    def __init__(self, color: Stone, name: str = "超级AI"):
        super().__init__(color, name)
        self.last_opponent_move: Optional[Position] = None
    
    def make_move(self, game) -> Position:
        """AI落子逻辑"""
        board = game.board
        size = board.size
        
        # 正常走棋逻辑
        # 优先选择与玩家上一手相邻的位置
        if self.last_opponent_move:
            adjacent_positions = self.last_opponent_move.get_adjacent_positions(size)
            # 过滤出合法的空位
            valid_adjacent = [
                pos for pos in adjacent_positions
                if board.is_empty(pos) and board.is_valid_move(pos, self.color)
            ]
            
            if valid_adjacent:
                # 随机选择一个相邻位置
                return random.choice(valid_adjacent)
        
        # 如果没有相邻位置或没有上一手，随机落子
        return self._random_move(board, size)
    
    def _random_move(self, board, size: int) -> Position:
        """随机选择一个合法位置"""
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

