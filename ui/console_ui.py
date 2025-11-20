"""
控制台UI
"""
from .builder import UIBuilder
from ..core.game import Game
from ..core.board import Board


class ConsoleUI:
    """控制台界面"""
    
    def __init__(self):
        self.builder = UIBuilder()
        self.show_hint = True
    
    def display(self, game: Game = None, message: str = ""):
        """显示界面"""
        self.builder.clear()
        
        if game:
            # 添加棋盘
            self.builder.add_board(game.board)
            
            # 添加游戏信息
            game_info = {
                'game_type': game.get_game_type(),
                'board_size': game.board.size,
                'current_player': game.current_player.name,
                'current_player_color': "黑" if game.current_player.color.value == 1 else "白",
                'game_over': game.game_over,
                'winner': game.winner.name if game.winner else None
            }
            self.builder.add_info(game_info)
        
        # 添加提示
        self.builder.add_prompt(self.show_hint)
        
        # 构建并显示
        ui_string = self.builder.build()
        print("\n" + "=" * 50)
        print(ui_string)
        if message:
            print(f"\n{message}")
        print("=" * 50 + "\n")
    
    def toggle_hint(self):
        """切换提示显示"""
        self.show_hint = not self.show_hint
    
    def show_message(self, message: str):
        """显示消息"""
        print(f"\n{message}\n")
    
    def show_error(self, error: str):
        """显示错误消息"""
        print(f"\n[错误] {error}\n")

