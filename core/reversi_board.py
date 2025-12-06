"""
Reversi (黑白棋) 棋盘
"""
from typing import List, Optional
from .board import Board
from .stone import Stone
from .position import Position


class ReversiBoard(Board):
    """黑白棋棋盘，负责合法性判定与翻转逻辑"""

    DIRECTIONS = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),          (0, 1),
        (1, -1),  (1, 0), (1, 1),
    ]

    def __init__(self, size: int):
        if size % 2 != 0 or size < 4:
            raise ValueError("Reversi board size must be even and >= 4")
        super().__init__(size)
        self._init_starting_stones()

    def _init_starting_stones(self):
        """在中心放置初始的四枚棋子"""
        mid1 = self.size // 2 - 1
        mid2 = self.size // 2
        centers = [
            (mid1, mid1, Stone.WHITE),
            (mid1, mid2, Stone.BLACK),
            (mid2, mid1, Stone.BLACK),
            (mid2, mid2, Stone.WHITE),
        ]
        for r, c, stone in centers:
            self.set_stone(Position(r, c), stone)

    def is_valid_move(self, position: Position, stone: Stone) -> bool:
        """检查落子是否能翻子且在空位上"""
        if not self.is_valid_position(position) or not self.is_empty(position):
            return False

        for dr, dc in self.DIRECTIONS:
            to_flip = self._collect_flips(position, stone, dr, dc)
            if to_flip:
                return True
        return False

    def place_stone(self, position: Position, stone: Stone) -> Optional[List[Position]]:
        """放置棋子并翻转被夹的对方棋子"""
        if not self.is_valid_move(position, stone):
            return None

        flipped: List[Position] = []
        for dr, dc in self.DIRECTIONS:
            flipped_dir = self._collect_flips(position, stone, dr, dc)
            flipped.extend(flipped_dir)

        self.set_stone(position, stone)
        for pos in flipped:
            self.set_stone(pos, stone)

        return flipped

    def _collect_flips(self, start: Position, stone: Stone, dr: int, dc: int) -> List[Position]:
        """沿某个方向收集可被翻转的棋子"""
        path: List[Position] = []
        r, c = start.row + dr, start.col + dc
        while 0 <= r < self.size and 0 <= c < self.size:
            pos = Position(r, c)
            current = self.get_stone(pos)
            if current == Stone.EMPTY:
                return []
            if current == stone:
                return path if path else []
            path.append(pos)
            r += dr
            c += dc
        return []

    def has_legal_move(self, stone: Stone) -> bool:
        """判断指定颜色是否还有合法落子"""
        for row in range(self.size):
            for col in range(self.size):
                if self.is_valid_move(Position(row, col), stone):
                    return True
        return False

    def is_full(self) -> bool:
        """棋盘是否已满"""
        for row in self._board:
            for stone in row:
                if stone == Stone.EMPTY:
                    return False
        return True

    def count_by_color(self) -> tuple[int, int]:
        """返回黑白棋子数量"""
        black = 0
        white = 0
        for row in self._board:
            for stone in row:
                if stone == Stone.BLACK:
                    black += 1
                elif stone == Stone.WHITE:
                    white += 1
        return black, white
