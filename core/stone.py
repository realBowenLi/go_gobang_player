"""
棋子枚举
"""
from enum import Enum


class Stone(Enum):
    """棋子类型"""
    EMPTY = 0
    BLACK = 1
    WHITE = 2
    
    def __str__(self):
        if self == Stone.EMPTY:
            return ". "  # 点+空格，占2个字符宽度
        elif self == Stone.BLACK:
            return "X "  # X+空格，占2个字符宽度
        else:
            return "O "  # O+空格，占2个字符宽度
    
    def opposite(self):
        """返回相反的棋子颜色"""
        if self == Stone.BLACK:
            return Stone.WHITE
        elif self == Stone.WHITE:
            return Stone.BLACK
        return Stone.EMPTY

