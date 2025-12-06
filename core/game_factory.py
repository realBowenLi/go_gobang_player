"""
游戏工厂
"""
from .game import Game
from .gobang_game import GobangGame
from .go_game import GoGame
from .reversi_game import ReversiGame
from .board import Board
from .gobang_board import GobangBoard
from .go_board import GoBoard
from .player import Player
from ..config import GameConfig
from ..exceptions import InvalidBoardSizeException


class GameFactory:
    """游戏工厂类"""

    @staticmethod
    def create_game(game_type: str, board_size: int, player1: Player, player2: Player) -> Game:
        """创建游戏实例"""
        if not GameConfig.validate_board_size(board_size):
            raise InvalidBoardSizeException(
                f"棋盘大小必须在{GameConfig.MIN_BOARD_SIZE}到{GameConfig.MAX_BOARD_SIZE}之间"
            )

        game = game_type.lower()
        if game in ["gobang", "五子棋"]:
            return GobangGame(board_size, player1, player2)
        if game in ["go", "围棋"]:
            return GoGame(board_size, player1, player2)
        if game in ["reversi", "黑白棋", "othello"]:
            return ReversiGame(board_size, player1, player2)
        raise ValueError(f"未知的游戏类型 {game_type}")

    @staticmethod
    def create_board(game_type: str, board_size: int) -> Board:
        """创建棋盘实例"""
        if not GameConfig.validate_board_size(board_size):
            raise InvalidBoardSizeException(
                f"棋盘大小必须在{GameConfig.MIN_BOARD_SIZE}到{GameConfig.MAX_BOARD_SIZE}之间"
            )

        game = game_type.lower()
        if game in ["gobang", "五子棋"]:
            return GobangBoard(board_size)
        if game in ["go", "围棋"]:
            return GoBoard(board_size)
        if game in ["reversi", "黑白棋", "othello"]:
            from .reversi_board import ReversiBoard
            return ReversiBoard(board_size)
        raise ValueError(f"未知的游戏类型 {game_type}")
