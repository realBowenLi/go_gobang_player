"""
UI建造者
"""
from typing import List
from .components import UIComponent, BoardComponent, InfoComponent, PromptComponent
from ..core.board import Board


class UIBuilder:
    """UI建造者（建造者模式）"""
    
    def __init__(self):
        self.components: List[UIComponent] = []
    
    def add_board(self, board: Board) -> 'UIBuilder':
        """添加棋盘组件"""
        self.components.append(BoardComponent(board))
        return self
    
    def add_info(self, game_info: dict) -> 'UIBuilder':
        """添加信息组件"""
        self.components.append(InfoComponent(game_info))
        return self
    
    def add_prompt(self, show_hint: bool = True) -> 'UIBuilder':
        """添加提示组件"""
        self.components.append(PromptComponent(show_hint))
        return self
    
    def build(self) -> str:
        """构建并返回完整的UI字符串"""
        parts = []
        for component in self.components:
            rendered = component.render()
            if rendered:
                parts.append(rendered)
        return "\n\n".join(parts)
    
    def clear(self):
        """清空组件"""
        self.components.clear()

