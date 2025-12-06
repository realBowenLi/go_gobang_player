"""
UI 组件
"""
from abc import ABC, abstractmethod
from typing import List
from ..core.board import Board
from ..core.position import Position
from ..core.stone import Stone


class UIComponent(ABC):
    @abstractmethod
    def render(self) -> str:
        pass


class BoardComponent(UIComponent):
    """棋盘渲染"""

    def __init__(self, board: Board):
        self.board = board
        self.show_coordinates = True

    def render(self) -> str:
        lines: List[str] = []
        size = self.board.size
        if self.show_coordinates:
            header = "   " + " ".join(str(i).rjust(2) for i in range(size))
            lines.append(header)
            lines.append("  " + "-" * (size * 3 + 1))

        for row in range(size):
            line = str(row).rjust(2) + "|" if self.show_coordinates else ""
            for col in range(size):
                pos = Position(row, col)
                stone = self.board.get_stone(pos)
                line += str(stone)
                if col < size - 1:
                    line += " "
            if self.show_coordinates:
                line += "|"
            lines.append(line)

        if self.show_coordinates:
            lines.append("  " + "-" * (size * 3 + 1))
            lines.append(header)
        return "\n".join(lines)


class InfoComponent(UIComponent):
    """游戏信息"""

    def __init__(self, game_info: dict):
        self.game_info = game_info

    def render(self) -> str:
        lines = []
        if 'game_type' in self.game_info:
            lines.append(f"游戏类型: {self.game_info['game_type']}")
        if 'board_size' in self.game_info:
            lines.append(f"棋盘大小: {self.game_info['board_size']}x{self.game_info['board_size']}")

        p1 = self.game_info.get("player1")
        p2 = self.game_info.get("player2")
        if p1:
            lines.append(f"黑方: {p1}")
        if p2:
            lines.append(f"白方: {p2}")

        if 'current_player' in self.game_info:
            player_name = self.game_info['current_player']
            player_color = self.game_info.get('current_player_color', '')
            lines.append(f"当前玩家: {player_name} ({player_color})")

        if 'game_over' in self.game_info and self.game_info['game_over']:
            if 'winner' in self.game_info and self.game_info['winner']:
                lines.append(f"游戏结束! 获胜者: {self.game_info['winner']}")
            else:
                lines.append("游戏结束! 平局")
        else:
            lines.append("游戏进行中...")
        return "\n".join(lines)


class PromptComponent(UIComponent):
    """提示命令"""

    def __init__(self, show_hint: bool = True):
        self.show_hint = show_hint
        self.hints = [
            "命令说明:",
            "  start <类型> <大小> human/ai/aivsai [color] [aiLv] [aiLv2]",
            "  place <行> <列> - 落子",
            "  pass - 虚着/跳过（围棋、黑白棋）",
            "  undo - 悔棋",
            "  resign - 认负",
            "  save <文件> / load <文件> / replay <文件>",
            "  register <用户> <密码> / login <用户> <密码>",
            "  restart - 重新开始",
            "  hint - 切换提示显示",
            "  quit - 退出游戏",
            "  示例: start gobang 15 human",
        ]

    def render(self) -> str:
        if not self.show_hint:
            return ""
        return "\n".join(self.hints)

    def toggle(self):
        self.show_hint = not self.show_hint
