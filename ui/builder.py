"""
UI 构建器（建造者模式）
"""
from typing import List
from .components import UIComponent, BoardComponent, InfoComponent, PromptComponent
from ..core.board import Board


class UIBuilder:
    """负责收集并渲染 UI 组件"""

    def __init__(self):
        self.components: List[UIComponent] = []

    def add_board(self, board: Board) -> 'UIBuilder':
        self.components.append(BoardComponent(board))
        return self

    def add_info(self, game_info: dict) -> 'UIBuilder':
        self.components.append(InfoComponent(game_info))
        return self

    def add_prompt(self, show_hint: bool = True) -> 'UIBuilder':
        self.components.append(PromptComponent(show_hint))
        return self

    def build(self) -> str:
        parts = []
        for component in self.components:
            rendered = component.render()
            if rendered:
                parts.append(rendered)
        return "\n\n".join(parts)

    def clear(self):
        self.components.clear()
