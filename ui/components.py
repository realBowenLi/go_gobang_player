"""
UI组件
"""
from abc import ABC, abstractmethod
from typing import List
from ..core.board import Board
from ..core.stone import Stone
from ..core.position import Position


class UIComponent(ABC):
    """UI组件抽象基类"""
    
    @abstractmethod
    def render(self) -> str:
        """渲染组件"""
        pass


class BoardComponent(UIComponent):
    """棋盘显示组件"""
    
    def __init__(self, board: Board):
        self.board = board
        self.show_coordinates = True
    
    def render(self) -> str:
        """渲染棋盘"""
        lines = []
        size = self.board.size
        
        # 顶部坐标
        if self.show_coordinates:
            # 每个数字占2个字符宽度，用空格分隔
            # 格式：3个空格 + " 0" + " " + " 1" + " " + ...
            header_parts = []
            for i in range(size):
                header_parts.append(str(i).rjust(2))
            header = "   " + " ".join(header_parts)
            lines.append(header)
            # 分隔线：2个空格 + size个位置，每个位置3个字符（数字2个+空格1个）
            lines.append("  " + "-" * (size * 3 + 1))
        
        # 棋盘内容
        for row in range(size):
            if self.show_coordinates:
                # 行号占2个字符，加上"|"，共3个字符，与顶部坐标的3个空格对齐
                line = str(row).rjust(2) + "|"
            else:
                line = ""
            
            for col in range(size):
                pos = Position(row, col)
                stone = self.board.get_stone(pos)
                stone_str = str(stone)
                # Stone的__str__已经确保每个位置都占用2个字符宽度
                # 空位返回 ". "（点+空格），黑子返回 "X "，白子返回 "O "
                line += stone_str
                
                # 如果不是最后一列，添加分隔空格（与顶部坐标格式一致）
                if col < size - 1:
                    line += " "
            
            if self.show_coordinates:
                line += "|"
            
            lines.append(line)
        
        # 底部坐标
        if self.show_coordinates:
            lines.append("  " + "-" * (size * 3 + 1))
            footer_parts = []
            for i in range(size):
                footer_parts.append(str(i).rjust(2))
            footer = "   " + " ".join(footer_parts)
            lines.append(footer)
        
        return "\n".join(lines)


class InfoComponent(UIComponent):
    """信息显示组件"""
    
    def __init__(self, game_info: dict):
        self.game_info = game_info
    
    def render(self) -> str:
        """渲染游戏信息"""
        lines = []
        
        if 'game_type' in self.game_info:
            game_type_name = "五子棋" if self.game_info['game_type'] == 'gobang' else "围棋"
            lines.append(f"游戏类型: {game_type_name}")
        
        if 'board_size' in self.game_info:
            lines.append(f"棋盘大小: {self.game_info['board_size']}x{self.game_info['board_size']}")
        
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
    """提示组件"""
    
    def __init__(self, show_hint: bool = True):
        self.show_hint = show_hint
        self.hints = [
            "命令说明:",
            "  start <游戏类型> <棋盘大小> <模式> [颜色] - 开始游戏 (模式: human/ai, 颜色: black/white)",
            "  place <行> <列> - 落子",
            "  pass - 虚着(仅围棋)",
            "  undo - 悔棋",
            "  resign - 投子认负",
            "  save <文件名> - 保存游戏",
            "  load <文件名> - 加载游戏",
            "  restart - 重新开始",
            "  hint - 显示/隐藏提示",
            "  quit - 退出游戏"
        ]
    
    def render(self) -> str:
        """渲染提示"""
        if not self.show_hint:
            return ""
        return "\n".join(self.hints)
    
    def toggle(self):
        """切换显示状态"""
        self.show_hint = not self.show_hint

