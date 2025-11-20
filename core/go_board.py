"""
围棋棋盘
"""
from typing import Optional, List, Set
from .board import Board
from .stone import Stone
from .position import Position


class GoBoard(Board):
    """围棋棋盘"""
    
    def __init__(self, size: int):
        super().__init__(size)
        self.last_move: Optional[Position] = None
        self.last_board_state: Optional[List[List[Stone]]] = None
    
    def is_valid_move(self, position: Position, stone: Stone) -> bool:
        """检查落子是否合法"""
        if not self.is_valid_position(position):
            return False
        if not self.is_empty(position):
            return False
        
        # 检查打劫（简单版本，只检查是否与上一步完全相同）
        if self.last_board_state is not None:
            # 临时放置棋子
            self.set_stone(position, stone)
            captured = self._capture_stones(position, stone.opposite())
            # 移除被提的棋子
            for pos in captured:
                self.set_stone(pos, Stone.EMPTY)
            
            # 检查是否与上一步状态相同（打劫）
            current_state = self.get_board_copy()
            is_ko = self._boards_equal(current_state, self.last_board_state)
            
            # 恢复状态
            self.set_stone(position, Stone.EMPTY)
            for pos in captured:
                self.set_stone(pos, stone.opposite())
            
            if is_ko:
                return False
        
        # 检查是否自杀（放置后自己无气且不能提子）
        self.set_stone(position, stone)
        captured = self._capture_stones(position, stone.opposite())
        has_liberty = self._has_liberty(position, stone)
        
        # 恢复状态
        self.set_stone(position, Stone.EMPTY)
        for pos in captured:
            self.set_stone(pos, stone.opposite())
        
        # 如果能提子或自己有气，则合法
        return len(captured) > 0 or has_liberty
    
    def place_stone(self, position: Position, stone: Stone) -> Optional[List[Position]]:
        """放置棋子，返回被提掉的棋子位置列表"""
        if not self.is_valid_move(position, stone):
            return None
        
        # 保存当前状态（用于打劫检测）
        self.last_board_state = self.get_board_copy()
        
        # 放置棋子
        self.set_stone(position, stone)
        self.last_move = position
        
        # 提子
        captured = self._capture_stones(position, stone.opposite())
        for pos in captured:
            self.set_stone(pos, Stone.EMPTY)
        
        return captured
    
    def _has_liberty(self, position: Position, stone: Stone) -> bool:
        """检查棋子是否有气（使用BFS）"""
        visited: Set[Position] = set()
        queue = [position]
        visited.add(position)
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        while queue:
            current = queue.pop(0)
            
            for dr, dc in directions:
                new_row = current.row + dr
                new_col = current.col + dc
                new_pos = Position(new_row, new_col)
                
                if not self.is_valid_position(new_pos):
                    continue
                
                if new_pos in visited:
                    continue
                
                new_stone = self.get_stone(new_pos)
                if new_stone == Stone.EMPTY:
                    return True  # 找到气
                elif new_stone == stone:
                    visited.add(new_pos)
                    queue.append(new_pos)
        
        return False
    
    def _capture_stones(self, position: Position, opponent_stone: Stone) -> List[Position]:
        """提掉无气的对手棋子"""
        captured: List[Position] = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            new_row = position.row + dr
            new_col = position.col + dc
            new_pos = Position(new_row, new_col)
            
            if not self.is_valid_position(new_pos):
                continue
            
            if self.get_stone(new_pos) != opponent_stone:
                continue
            
            # 检查这个棋子组是否有气
            if not self._has_liberty(new_pos, opponent_stone):
                # 收集所有相连的无气棋子
                group = self._get_connected_group(new_pos, opponent_stone)
                for pos in group:
                    if pos not in captured:
                        captured.append(pos)
        
        return captured
    
    def _get_connected_group(self, position: Position, stone: Stone) -> List[Position]:
        """获取相连的棋子组"""
        group: List[Position] = []
        visited: Set[Position] = set()
        queue = [position]
        visited.add(position)
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        while queue:
            current = queue.pop(0)
            group.append(current)
            
            for dr, dc in directions:
                new_row = current.row + dr
                new_col = current.col + dc
                new_pos = Position(new_row, new_col)
                
                if not self.is_valid_position(new_pos):
                    continue
                
                if new_pos in visited:
                    continue
                
                if self.get_stone(new_pos) == stone:
                    visited.add(new_pos)
                    queue.append(new_pos)
        
        return group
    
    def _boards_equal(self, board1: List[List[Stone]], board2: List[List[Stone]]) -> bool:
        """比较两个棋盘状态是否相同"""
        if len(board1) != len(board2):
            return False
        for i in range(len(board1)):
            if len(board1[i]) != len(board2[i]):
                return False
            for j in range(len(board1[i])):
                if board1[i][j] != board2[i][j]:
                    return False
        return True
    
    def calculate_territory(self) -> tuple[int, int]:
        """计算双方领地（简单版本：数子法）"""
        black_count = 0
        white_count = 0
        
        for row in self._board:
            for stone in row:
                if stone == Stone.BLACK:
                    black_count += 1
                elif stone == Stone.WHITE:
                    white_count += 1
        
        return black_count, white_count

