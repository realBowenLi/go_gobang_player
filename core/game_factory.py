"""
游戏工厂
"""
from .game import Game
from .gobang_game import GobangGame
from .go_game import GoGame
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
        
        if game_type.lower() == "gobang" or game_type.lower() == "五子棋":
            return GobangGame(board_size, player1, player2)
        elif game_type.lower() == "go" or game_type.lower() == "围棋":
            return GoGame(board_size, player1, player2)
        else:
            raise ValueError(f"未知的游戏类型: {game_type}")
    
    @staticmethod
    def create_board(game_type: str, board_size: int) -> Board:
        """创建棋盘实例"""
        if not GameConfig.validate_board_size(board_size):
            raise InvalidBoardSizeException(
                f"棋盘大小必须在{GameConfig.MIN_BOARD_SIZE}到{GameConfig.MAX_BOARD_SIZE}之间"
            )
        
        if game_type.lower() == "gobang" or game_type.lower() == "五子棋":
            return GobangBoard(board_size)
        elif game_type.lower() == "go" or game_type.lower() == "围棋":
            return GoBoard(board_size)
        else:
            raise ValueError(f"未知的游戏类型: {game_type}")

