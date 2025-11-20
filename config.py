"""
配置管理
"""


class GameConfig:
    """游戏配置类（单例模式）"""
    _instance = None
    
    MIN_BOARD_SIZE = 8
    MAX_BOARD_SIZE = 19
    DEFAULT_BOARD_SIZE = 15
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameConfig, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def validate_board_size(cls, size: int) -> bool:
        """验证棋盘大小是否合法"""
        return cls.MIN_BOARD_SIZE <= size <= cls.MAX_BOARD_SIZE

