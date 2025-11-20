"""
具体命令类
"""
from typing import Optional
from .command import Command
from ..core.position import Position
from ..exceptions import InvalidInputException, NoHistoryException


class StartGameCommand(Command):
    """开始游戏命令"""
    
    def __init__(self, controller, game_type: str, board_size: int, 
                 mode: str, human_color: Optional[str] = None):
        self.controller = controller
        self.game_type = game_type
        self.board_size = board_size
        self.mode = mode  # "human" 或 "ai"
        self.human_color = human_color
    
    def execute(self) -> str:
        """执行开始游戏"""
        return self.controller.start_game(self.game_type, self.board_size, 
                                         self.mode, self.human_color)
    
    def can_undo(self) -> bool:
        return False
    
    def undo(self):
        pass


class PlaceStoneCommand(Command):
    """落子命令"""
    
    def __init__(self, controller, position: Position):
        self.controller = controller
        self.position = position
    
    def execute(self) -> str:
        """执行落子"""
        return self.controller.place_stone(self.position)
    
    def can_undo(self) -> bool:
        return False
    
    def undo(self):
        pass


class PassCommand(Command):
    """虚着命令（仅围棋）"""
    
    def __init__(self, controller):
        self.controller = controller
    
    def execute(self) -> str:
        """执行虚着"""
        return self.controller.pass_move()
    
    def can_undo(self) -> bool:
        return False
    
    def undo(self):
        pass


class UndoCommand(Command):
    """悔棋命令"""
    
    def __init__(self, controller):
        self.controller = controller
    
    def execute(self) -> str:
        """执行悔棋"""
        try:
            return self.controller.undo_move()
        except NoHistoryException as e:
            return str(e)
    
    def can_undo(self) -> bool:
        return False
    
    def undo(self):
        pass


class ResignCommand(Command):
    """投子认负命令"""
    
    def __init__(self, controller):
        self.controller = controller
    
    def execute(self) -> str:
        """执行认负"""
        return self.controller.resign()
    
    def can_undo(self) -> bool:
        return False
    
    def undo(self):
        pass


class SaveCommand(Command):
    """保存游戏命令"""
    
    def __init__(self, controller, filename: str):
        self.controller = controller
        self.filename = filename
    
    def execute(self) -> str:
        """执行保存"""
        try:
            return self.controller.save_game(self.filename)
        except Exception as e:
            return f"保存失败: {str(e)}"
    
    def can_undo(self) -> bool:
        return False
    
    def undo(self):
        pass


class LoadCommand(Command):
    """加载游戏命令"""
    
    def __init__(self, controller, filename: str):
        self.controller = controller
        self.filename = filename
    
    def execute(self) -> str:
        """执行加载"""
        try:
            return self.controller.load_game(self.filename)
        except Exception as e:
            return f"加载失败: {str(e)}"
    
    def can_undo(self) -> bool:
        return False
    
    def undo(self):
        pass


class RestartCommand(Command):
    """重新开始游戏命令"""
    
    def __init__(self, controller):
        self.controller = controller
    
    def execute(self) -> str:
        """执行重新开始"""
        return self.controller.restart_game()
    
    def can_undo(self) -> bool:
        return False
    
    def undo(self):
        pass

