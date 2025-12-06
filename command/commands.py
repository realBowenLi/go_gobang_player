"""
具体命令
"""
from typing import Optional
from .command import Command
from ..core.position import Position
from ..exceptions import NoHistoryException


class StartGameCommand(Command):
    """开始游戏命令"""

    def __init__(self, controller, game_type: str, board_size: int,
                 mode: str, human_color: Optional[str] = None,
                 ai_level: int = 2, ai2_level: Optional[int] = None):
        self.controller = controller
        self.game_type = game_type
        self.board_size = board_size
        self.mode = mode  # human / ai / aivsai
        self.human_color = human_color
        self.ai_level = ai_level
        self.ai2_level = ai2_level

    def execute(self) -> str:
        return self.controller.start_game(
            self.game_type,
            self.board_size,
            self.mode,
            self.human_color,
            self.ai_level,
            self.ai2_level,
        )

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
        return self.controller.place_stone(self.position)

    def can_undo(self) -> bool:
        return False

    def undo(self):
        pass


class PassCommand(Command):
    """虚着/跳过（围棋、黑白棋）"""

    def __init__(self, controller):
        self.controller = controller

    def execute(self) -> str:
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
        return self.controller.restart_game()

    def can_undo(self) -> bool:
        return False

    def undo(self):
        pass


class RegisterCommand(Command):
    """注册账号"""

    def __init__(self, controller, username: str, password: str):
        self.controller = controller
        self.username = username
        self.password = password

    def execute(self) -> str:
        return self.controller.register_account(self.username, self.password)

    def can_undo(self) -> bool:
        return False

    def undo(self):
        pass


class LoginCommand(Command):
    """登录账号（仅单用户）"""

    def __init__(self, controller, username: str, password: str):
        self.controller = controller
        self.username = username
        self.password = password

    def execute(self) -> str:
        return self.controller.login_account(self.username, self.password)

    def can_undo(self) -> bool:
        return False

    def undo(self):
        pass


class ReplayCommand(Command):
    """回放录像命令"""

    def __init__(self, controller, filename: str):
        self.controller = controller
        self.filename = filename

    def execute(self) -> str:
        return self.controller.replay_game(self.filename)

    def can_undo(self) -> bool:
        return False

    def undo(self):
        pass
