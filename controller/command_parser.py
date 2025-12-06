"""
命令解析器
"""
from typing import Optional
from ..command.commands import (
    Command, StartGameCommand, PlaceStoneCommand, PassCommand,
    UndoCommand, ResignCommand, SaveCommand, LoadCommand,
    RestartCommand, RegisterCommand, LoginCommand, ReplayCommand
)
from ..core.position import Position
from ..exceptions import InvalidInputException
from ..config import GameConfig


class CommandParser:
    """命令解析器"""

    def __init__(self, controller):
        self.controller = controller

    def parse(self, input_str: str) -> Optional[Command]:
        if not input_str:
            return None

        parts = input_str.strip().split()
        if not parts:
            return None

        command_name = parts[0].lower()

        try:
            if command_name == "start":
                return self._parse_start(parts[1:])
            if command_name == "place":
                return self._parse_place(parts[1:])
            if command_name == "pass":
                return PassCommand(self.controller)
            if command_name == "undo":
                return UndoCommand(self.controller)
            if command_name == "resign":
                return ResignCommand(self.controller)
            if command_name == "save":
                return self._parse_save(parts[1:])
            if command_name == "load":
                return self._parse_load(parts[1:])
            if command_name == "restart":
                return RestartCommand(self.controller)
            if command_name == "register":
                return self._parse_register(parts[1:])
            if command_name == "login":
                return self._parse_login(parts[1:])
            if command_name == "replay":
                return self._parse_replay(parts[1:])
            if command_name in ["hint", "quit", "exit"]:
                return None
            raise InvalidInputException(f"未知命令: {command_name}")
        except (IndexError, ValueError) as e:
            raise InvalidInputException(f"命令格式错误: {str(e)}")

    def _parse_start(self, args: list) -> StartGameCommand:
        if len(args) < 2:
            raise InvalidInputException("start命令格式: start <游戏类型> <棋盘大小> <模式> [其他参数]")

        game_type = args[0]
        try:
            board_size = int(args[1])
        except ValueError:
            raise InvalidInputException("棋盘大小必须是数字")
        board_size = board_size if board_size > 0 else GameConfig.default_size_for(game_type)

        if len(args) < 3:
            raise InvalidInputException("缺少模式参数 human/ai/aivsai")
        mode = args[2].lower()
        if mode not in ["human", "ai", "aivsai"]:
            raise InvalidInputException("模式必须是 human / ai / aivsai")

        human_color = None
        ai_level = 2
        ai2_level = None

        if mode == "ai":
            if len(args) >= 4:
                human_color = args[3].lower()
                if human_color not in ["black", "white"]:
                    raise InvalidInputException("颜色必须是 black 或 white")
            if len(args) >= 5:
                ai_level = int(args[4])
        elif mode == "aivsai":
            if len(args) >= 4:
                ai_level = int(args[3])
            if len(args) >= 5:
                ai2_level = int(args[4])

        return StartGameCommand(
            self.controller,
            game_type,
            board_size,
            mode,
            human_color,
            ai_level,
            ai2_level,
        )

    def _parse_place(self, args: list) -> PlaceStoneCommand:
        if len(args) < 2:
            raise InvalidInputException("place命令格式: place <行> <列>")
        try:
            row = int(args[0])
            col = int(args[1])
        except ValueError:
            raise InvalidInputException("行和列必须是数字")
        position = Position(row, col)
        return PlaceStoneCommand(self.controller, position)

    def _parse_save(self, args: list) -> SaveCommand:
        if len(args) < 1:
            raise InvalidInputException("save命令格式: save <文件名>")
        filename = args[0]
        return SaveCommand(self.controller, filename)

    def _parse_load(self, args: list) -> LoadCommand:
        if len(args) < 1:
            raise InvalidInputException("load命令格式: load <文件名>")
        filename = args[0]
        return LoadCommand(self.controller, filename)

    def _parse_register(self, args: list) -> RegisterCommand:
        if len(args) < 2:
            raise InvalidInputException("register命令格式: register <用户名> <密码>")
        return RegisterCommand(self.controller, args[0], args[1])

    def _parse_login(self, args: list) -> LoginCommand:
        if len(args) < 2:
            raise InvalidInputException("login命令格式: login <用户名> <密码>")
        return LoginCommand(self.controller, args[0], args[1])

    def _parse_replay(self, args: list) -> ReplayCommand:
        if len(args) < 1:
            raise InvalidInputException("replay命令格式: replay <文件名>")
        return ReplayCommand(self.controller, args[0])
