"""
自定义异常类
"""

class GameException(Exception):
    """游戏基础异常"""
    pass


class InvalidMoveException(GameException):
    """无效落子异常"""
    pass


class GameOverException(GameException):
    """游戏已结束异常"""
    pass


class FileOperationException(GameException):
    """文件操作异常"""
    pass


class InvalidInputException(GameException):
    """无效输入异常"""
    pass


class InvalidBoardSizeException(GameException):
    """无效棋盘大小异常"""
    pass


class NoHistoryException(GameException):
    """无历史记录异常（悔棋时）"""
    pass

