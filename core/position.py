"""
位置类（值对象）
"""


class Position:
    """棋盘位置"""
    
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
    
    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.row == other.row and self.col == other.col
    
    def __hash__(self):
        return hash((self.row, self.col))
    
    def __repr__(self):
        return f"Position({self.row}, {self.col})"
    
    def __str__(self):
        return f"({self.row}, {self.col})"
    
    def is_adjacent(self, other) -> bool:
        """判断两个位置是否相邻（上下左右）"""
        if not isinstance(other, Position):
            return False
        row_diff = abs(self.row - other.row)
        col_diff = abs(self.col - other.col)
        return (row_diff == 1 and col_diff == 0) or (row_diff == 0 and col_diff == 1)
    
    def get_adjacent_positions(self, board_size: int):
        """获取相邻位置列表"""
        adjacent = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            new_row = self.row + dr
            new_col = self.col + dc
            if 0 <= new_row < board_size and 0 <= new_col < board_size:
                adjacent.append(Position(new_row, new_col))
        return adjacent

