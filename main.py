"""
主程序入口（控制台）
"""
import sys
import os
from pathlib import Path

# 兼容直接执行 python main.py：确保包可见并设置包名
if __package__ in (None, ""):
    current_dir = Path(__file__).resolve().parent
    parent_dir = current_dir.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    __package__ = current_dir.name

try:
    from .controller.game_controller import GameController
    from .controller.command_parser import CommandParser
    from .ui.console_ui import ConsoleUI
    from .exceptions import InvalidInputException
except ImportError as e:
    print(f"导入错误: {e}")
    sys.exit(1)


def drive_ai(controller: GameController, ui: ConsoleUI):
    """连续驱动 AI 直到轮到人类或对局结束"""
    game = controller.get_game()
    while controller.is_ai_turn() and game and not game.game_over:
        ai_result = controller.make_ai_move()
        ui.show_message(f"[AI] {ai_result}")
        game = controller.get_game()


def main():
    controller = GameController()
    parser = CommandParser(controller)
    ui = ConsoleUI()

    print("=" * 50)
    print("欢迎来到棋类对战平台!")
    print("支持五子棋、围棋、黑白棋的人机/双人/AI对战")
    print("=" * 50)

    ui.display()

    running = True
    while running:
        try:
            user_input = input("请输入命令: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["quit", "exit", "q"]:
                print("感谢使用，再见!")
                break
            if user_input.lower() == "hint":
                ui.toggle_hint()
                ui.display(controller.get_game())
                continue

            try:
                command = parser.parse(user_input)
            except InvalidInputException as e:
                ui.show_error(str(e))
                continue

            if command is None:
                continue

            result = command.execute()
            if result:
                ui.show_message(result)

            drive_ai(controller, ui)

            game = controller.get_game()
            if game:
                ui.display(game)
                if game.game_over:
                    if game.winner:
                        ui.show_message(f"游戏结束! 获胜者: {game.winner.name}")
                    else:
                        ui.show_message("游戏结束! 平局!")
            else:
                ui.display()
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            running = False
        except Exception as e:
            ui.show_error(f"发生错误: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
