"""
围棋游戏
"""
from typing import Optional
from .game import Game
from .board import Board
from .go_board import GoBoard
from .player import Player
from .position import Position
from ..exceptions import InvalidMoveException


class GoGame(Game):
    """围棋游戏"""
    
    def __init__(self, board_size: int, player1: Player, player2: Player):
        board = GoBoard(board_size)
        super().__init__(board, player1, player2)
        self.consecutive_passes = 0  # 连续虚着次数
    
    def get_game_type(self) -> str:
        return "go"
    
    def _supports_pass(self) -> bool:
        return True
    
    def _handle_pass(self) -> bool:
        """处理虚着"""
        # 检查是否是AI玩家，AI不能虚着
        from .ai_player import SuperAI
        if isinstance(self.current_player, SuperAI):
            raise InvalidMoveException("AI不能虚着")
        
        self.consecutive_passes += 1
        
        # 如果双方都虚着，游戏结束
        if self.consecutive_passes >= 2:
            self.game_over = True
            self._determine_winner()
            return False
        
        # 切换玩家
        self._switch_player()
        return True
    
    def make_move(self, position: Optional[Position] = None) -> bool:
        """重写make_move以处理虚着后的连续虚着计数"""
        if position is not None:
            self.consecutive_passes = 0  # 有落子则重置虚着计数
        return super().make_move(position)
    
    def _check_win_condition(self, position: Position) -> bool:
        """围棋不通过落子直接判断胜负"""
        return False
    
    def _check_draw(self) -> bool:
        """围棋不通过棋盘满判断平局"""
        return False
    
    def _determine_winner(self):
        """判断胜负（数子法）"""
        if isinstance(self.board, GoBoard):
            black_count, white_count = self.board.calculate_territory()
            
            # 简单判断：棋子多的一方获胜
            # 实际围棋规则更复杂，这里简化处理
            if black_count > white_count:
                self.winner = self.player1 if self.player1.color.value == 1 else self.player2
            elif white_count > black_count:
                self.winner = self.player1 if self.player1.color.value == 2 else self.player2
            else:
                self.winner = None  # 平局

