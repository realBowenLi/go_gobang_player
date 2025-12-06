"""
配置管理
"""


class GameConfig:
    """游戏配置类（单例模式）"""
    _instance = None
    
    MIN_BOARD_SIZE = 8
    MAX_BOARD_SIZE = 19
    DEFAULT_BOARD_SIZE = 15
    DEFAULT_SIZES = {
        "gobang": 15,
        "go": 19,
        "reversi": 8,
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameConfig, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def validate_board_size(cls, size: int) -> bool:
        """验证棋盘大小是否合法"""
        return cls.MIN_BOARD_SIZE <= size <= cls.MAX_BOARD_SIZE
    
    @classmethod
    def default_size_for(cls, game_type: str) -> int:
        return cls.DEFAULT_SIZES.get(game_type.lower(), cls.DEFAULT_BOARD_SIZE)

