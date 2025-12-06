"""
黑白棋游戏
"""
from typing import Optional
from .game import Game
from .reversi_board import ReversiBoard
from .player import Player
from .position import Position
from .stone import Stone
from ..exceptions import InvalidMoveException


class ReversiGame(Game):
    """黑白棋游戏逻辑"""

    def __init__(self, board_size: int, player1: Player, player2: Player):
        board = ReversiBoard(board_size)
        super().__init__(board, player1, player2)
        self.consecutive_passes = 0
        self.forced_pass_message: Optional[str] = None

    def get_game_type(self) -> str:
        return "reversi"

    def _supports_pass(self) -> bool:
        return True

    def _handle_pass(self) -> bool:
        """黑白棋只有无合法落子时才允许（或被迫）虚着"""
        if self._current_has_move():
            raise InvalidMoveException("当前仍有合法落子，不能虚着")
        self.consecutive_passes += 1
        if self.consecutive_passes >= 2:
            self._determine_winner()
            self.game_over = True
            return False
        skipped = self.current_player
        self._switch_player()
        self.forced_pass_message = f"{skipped.name} 无合法棋步，被迫跳过"
        return True

    def make_move(self, position: Optional[Position] = None) -> bool:
        """处理落子/跳过以及连续无手的结束判定"""
        if self.game_over:
            from ..exceptions import GameOverException
            raise GameOverException("游戏已结束")

        self.forced_pass_message = None

        if position is None:
            return self._handle_pass()

        if not isinstance(self.board, ReversiBoard):
            raise InvalidMoveException("棋盘类型错误")

        if not self.board.is_valid_move(position, self.current_player.color):
            raise InvalidMoveException(f"无效的落子位置 {position}")

        # 保存状态供悔棋/回放
        self._save_state()
        self._record_move(self.current_player, position)

        # 落子并翻转
        self.board.place_stone(position, self.current_player.color)
        self.last_move = position
        self.consecutive_passes = 0

        # 结束条件：棋盘满或双方都无合法落子
        if self.board.is_full() or (not self.board.has_legal_move(Stone.BLACK) and not self.board.has_legal_move(Stone.WHITE)):
            self._determine_winner()
            self.game_over = True
            return False

        # 切换玩家，如下一玩家无棋可下，自动跳过一回合
        self._switch_player()
        if not self.board.has_legal_move(self.current_player.color):
            self.consecutive_passes += 1
            if self.consecutive_passes >= 2:
                self._determine_winner()
                self.game_over = True
                return False
            skip_player = self.current_player
            # 记录被迫跳过
            self._record_move(skip_player, None)
            self._switch_player()
            self.forced_pass_message = f"{skip_player.name} 无合法棋步，本回合被跳过"
        else:
            self.consecutive_passes = 0

        return True

    def _current_has_move(self) -> bool:
        if isinstance(self.board, ReversiBoard):
            return self.board.has_legal_move(self.current_player.color)
        return False

    def _check_win_condition(self, position: Position) -> bool:
        """胜负在终局统一判断"""
        return False

    def _check_draw(self) -> bool:
        return False

    def _determine_winner(self):
        if isinstance(self.board, ReversiBoard):
            black, white = self.board.count_by_color()
            if black > white:
                self.winner = self.player1 if self.player1.color == Stone.BLACK else self.player2
            elif white > black:
                self.winner = self.player1 if self.player1.color == Stone.WHITE else self.player2
            else:
                self.winner = None
