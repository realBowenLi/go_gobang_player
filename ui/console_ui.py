"""
控制台 UI
"""
from .builder import UIBuilder
from ..core.game import Game
from ..core.stone import Stone


class ConsoleUI:
    """简单的控制台渲染"""

    def __init__(self):
        self.builder = UIBuilder()
        self.show_hint = True

    def display(self, game: Game = None, message: str = ""):
        self.builder.clear()

        if game:
            self.builder.add_board(game.board)
            game_info = {
                'game_type': game.get_game_type(),
                'board_size': game.board.size,
                'current_player': game.current_player.name,
                'current_player_color': "黑" if game.current_player.color == Stone.BLACK else "白",
                'game_over': game.game_over,
                'winner': game.winner.name if game.winner else None,
                'player1': self._player_line(game.player1),
                'player2': self._player_line(game.player2),
            }
            self.builder.add_info(game_info)

        self.builder.add_prompt(self.show_hint)
        ui_string = self.builder.build()
        print("\n" + "=" * 50)
        print(ui_string)
        if message:
            print(f"\n{message}")
        print("=" * 50 + "\n")

    def toggle_hint(self):
        self.show_hint = not self.show_hint

    def show_message(self, message: str):
        print(f"\n{message}\n")

    def show_error(self, error: str):
        print(f"\n[错误] {error}\n")

    def _player_line(self, player) -> str:
        profile = getattr(player, "profile", {}) or {}
        stats = profile.get("stats", {})
        stats_str = ""
        if stats:
            stats_str = f" (战绩: {stats.get('wins', 0)}/{stats.get('games', 0)})"
        role = ""
        if profile.get("is_ai"):
            role = f"AI Lv{profile.get('ai_level', '')}"
        elif profile.get("is_guest"):
            role = "游客"
        else:
            role = profile.get("username", "")
        name = player.name if player.name else role
        return f"{name} {role}{stats_str}"
