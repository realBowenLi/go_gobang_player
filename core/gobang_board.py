"""
五子棋棋盘
"""
from typing import Optional, List
from .board import Board
from .stone import Stone
from .position import Position


class GobangBoard(Board):
    """五子棋棋盘"""
    
    def is_valid_move(self, position: Position, stone: Stone) -> bool:
        """检查落子是否合法"""
        if not self.is_valid_position(position):
            return False
        if not self.is_empty(position):
            return False
        return True
    
    def place_stone(self, position: Position, stone: Stone) -> Optional[List[Position]]:
        """放置棋子（五子棋不涉及提子）"""
        if not self.is_valid_move(position, stone):
            return None
        self.set_stone(position, stone)
        return []
    
    def check_win(self, position: Position, stone: Stone) -> bool:
        """检查是否连成五子"""
        directions = [
            (0, 1),   # 横向
            (1, 0),   # 纵向
            (1, 1),   # 主对角线
            (1, -1)   # 副对角线
        ]
        
        for dr, dc in directions:
            count = 1  # 包括当前棋子
            
            # 正向检查
            for i in range(1, 5):
                new_row = position.row + dr * i
                new_col = position.col + dc * i
                if (0 <= new_row < self.size and 
                    0 <= new_col < self.size and 
                    self.get_stone(Position(new_row, new_col)) == stone):
                    count += 1
                else:
                    break
            
            # 反向检查
            for i in range(1, 5):
                new_row = position.row - dr * i
                new_col = position.col - dc * i
                if (0 <= new_row < self.size and 
                    0 <= new_col < self.size and 
                    self.get_stone(Position(new_row, new_col)) == stone):
                    count += 1
                else:
                    break
            
            if count >= 5:
                return True
        
        return False
    
    def is_full(self) -> bool:
        """检查棋盘是否已满"""
        return self.count_stones() == self.size * self.size

