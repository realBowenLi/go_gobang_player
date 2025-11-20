"""
棋盘抽象基类
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from .stone import Stone
from .position import Position


class Board(ABC):
    """棋盘抽象基类"""
    
    def __init__(self, size: int):
        self.size = size
        self._board = [[Stone.EMPTY for _ in range(size)] for _ in range(size)]
    
    def get_stone(self, position: Position) -> Stone:
        """获取指定位置的棋子"""
        if not self.is_valid_position(position):
            raise ValueError(f"Invalid position: {position}")
        return self._board[position.row][position.col]
    
    def set_stone(self, position: Position, stone: Stone):
        """在指定位置放置棋子"""
        if not self.is_valid_position(position):
            raise ValueError(f"Invalid position: {position}")
        self._board[position.row][position.col] = stone
    
    def is_valid_position(self, position: Position) -> bool:
        """检查位置是否在棋盘范围内"""
        return 0 <= position.row < self.size and 0 <= position.col < self.size
    
    def is_empty(self, position: Position) -> bool:
        """检查位置是否为空"""
        return self.get_stone(position) == Stone.EMPTY
    
    def clear(self):
        """清空棋盘"""
        self._board = [[Stone.EMPTY for _ in range(self.size)] for _ in range(self.size)]
    
    def get_board_copy(self) -> List[List[Stone]]:
        """获取棋盘副本"""
        return [row[:] for row in self._board]
    
    def set_board(self, board: List[List[Stone]]):
        """设置棋盘状态"""
        if len(board) != self.size or any(len(row) != self.size for row in board):
            raise ValueError("Board size mismatch")
        self._board = [row[:] for row in board]
    
    def count_stones(self) -> int:
        """统计棋盘上的棋子数量"""
        count = 0
        for row in self._board:
            for stone in row:
                if stone != Stone.EMPTY:
                    count += 1
        return count
    
    @abstractmethod
    def is_valid_move(self, position: Position, stone: Stone) -> bool:
        """检查落子是否合法（子类实现）"""
        pass
    
    @abstractmethod
    def place_stone(self, position: Position, stone: Stone) -> Optional[List[Position]]:
        """放置棋子，返回被提掉的棋子位置列表（如果有）"""
        pass

