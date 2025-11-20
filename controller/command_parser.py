"""
命令解析器
"""
from typing import Optional, Tuple
from ..command.commands import (
    Command, StartGameCommand, PlaceStoneCommand, PassCommand,
    UndoCommand, ResignCommand, SaveCommand, LoadCommand, RestartCommand
)
from ..core.position import Position
from ..exceptions import InvalidInputException


class CommandParser:
    """命令解析器"""
    
    def __init__(self, controller):
        self.controller = controller
    
    def parse(self, input_str: str) -> Optional[Command]:
        """解析用户输入并返回命令对象"""
        if not input_str:
            return None
        
        parts = input_str.strip().split()
        if not parts:
            return None
        
        command_name = parts[0].lower()
        
        try:
            if command_name == "start":
                return self._parse_start(parts[1:])
            elif command_name == "place":
                return self._parse_place(parts[1:])
            elif command_name == "pass":
                return PassCommand(self.controller)
            elif command_name == "undo":
                return UndoCommand(self.controller)
            elif command_name == "resign":
                return ResignCommand(self.controller)
            elif command_name == "save":
                return self._parse_save(parts[1:])
            elif command_name == "load":
                return self._parse_load(parts[1:])
            elif command_name == "restart":
                return RestartCommand(self.controller)
            elif command_name == "hint":
                return None  # 特殊处理，不返回命令
            elif command_name == "quit" or command_name == "exit":
                return None  # 特殊处理
            else:
                raise InvalidInputException(f"未知命令: {command_name}")
        except (IndexError, ValueError) as e:
            raise InvalidInputException(f"命令格式错误: {str(e)}")
    
    def _parse_start(self, args: list) -> StartGameCommand:
        """解析开始游戏命令"""
        if len(args) < 3:
            raise InvalidInputException("start命令格式: start <游戏类型> <棋盘大小> <模式> [颜色]")
        
        game_type = args[0]
        try:
            board_size = int(args[1])
        except ValueError:
            raise InvalidInputException("棋盘大小必须是数字")
        
        mode = args[2].lower()
        if mode not in ["human", "ai"]:
            raise InvalidInputException("模式必须是 'human' 或 'ai'")
        
        human_color = None
        if mode == "ai" and len(args) >= 4:
            human_color = args[3].lower()
            if human_color not in ["black", "white"]:
                raise InvalidInputException("颜色必须是 'black' 或 'white'")
        
        return StartGameCommand(self.controller, game_type, board_size, mode, human_color)
    
    def _parse_place(self, args: list) -> PlaceStoneCommand:
        """解析落子命令"""
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
        """解析保存命令"""
        if len(args) < 1:
            raise InvalidInputException("save命令格式: save <文件名>")
        
        filename = args[0]
        return SaveCommand(self.controller, filename)
    
    def _parse_load(self, args: list) -> LoadCommand:
        """解析加载命令"""
        if len(args) < 1:
            raise InvalidInputException("load命令格式: load <文件名>")
        
        filename = args[0]
        return LoadCommand(self.controller, filename)

