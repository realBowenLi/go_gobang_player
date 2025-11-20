"""
五子棋游戏
"""
from typing import Optional
from .game import Game
from .board import Board
from .gobang_board import GobangBoard
from .player import Player
from .position import Position


class GobangGame(Game):
    """五子棋游戏"""
    
    def __init__(self, board_size: int, player1: Player, player2: Player):
        board = GobangBoard(board_size)
        super().__init__(board, player1, player2)
    
    def get_game_type(self) -> str:
        return "gobang"
    
    def _supports_pass(self) -> bool:
        return False
    
    def _handle_pass(self) -> bool:
        raise NotImplementedError("五子棋不支持虚着")
    
    def _check_win_condition(self, position: Position) -> bool:
        """检查是否连成五子"""
        if isinstance(self.board, GobangBoard):
            return self.board.check_win(position, self.current_player.color)
        return False
    
    def _check_draw(self) -> bool:
        """检查是否平局（棋盘被占满）"""
        if isinstance(self.board, GobangBoard):
            return self.board.is_full()
        return False

