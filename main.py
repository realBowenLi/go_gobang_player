"""
主程序入口
"""
import sys
import os

# 添加当前目录到路径，以便导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# 使用相对导入（从go_gobang_player包内运行）
try:
    from controller.game_controller import GameController
    from controller.command_parser import CommandParser
    from ui.console_ui import ConsoleUI
    from exceptions import InvalidInputException
except ImportError:
    # 如果相对导入失败，尝试绝对导入（从项目根目录运行）
    try:
        from go_gobang_player.controller.game_controller import GameController
        from go_gobang_player.controller.command_parser import CommandParser
        from go_gobang_player.ui.console_ui import ConsoleUI
        from go_gobang_player.exceptions import InvalidInputException
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保在正确的目录下运行程序")
        sys.exit(1)


def main():
    """主函数"""
    controller = GameController()
    parser = CommandParser(controller)
    ui = ConsoleUI()
    
    print("=" * 50)
    print("欢迎来到棋类对战平台!")
    print("支持五子棋和围棋的人机对战和本地双人对战")
    print("=" * 50)
    
    # 显示初始界面
    ui.display()
    
    running = True
    while running:
        try:
            # 获取用户输入
            user_input = input("请输入命令: ").strip()
            
            if not user_input:
                continue
            
            # 处理特殊命令
            if user_input.lower() in ["quit", "exit", "q"]:
                print("感谢使用，再见!")
                running = False
                continue
            
            if user_input.lower() == "hint":
                ui.toggle_hint()
                ui.display(controller.get_game())
                continue
            
            # 解析命令
            try:
                command = parser.parse(user_input)
            except InvalidInputException as e:
                ui.show_error(str(e))
                continue
            
            if command is None:
                continue
            
            # 执行命令
            result = command.execute()
            
            # 显示结果
            if result:
                ui.show_message(result)
            
            # 如果是AI回合，自动执行AI落子
            if controller.is_ai_turn() and controller.get_game() and not controller.get_game().game_over:
                ai_result = controller.make_ai_move()
                if ai_result:
                    ui.show_message(f"[AI] {ai_result}")
            
            # 显示游戏界面
            game = controller.get_game()
            if game:
                ui.display(game)
            else:
                ui.display()
            
            # 如果游戏结束，显示结束信息
            if game and game.game_over:
                if game.winner:
                    ui.show_message(f"游戏结束! 获胜者: {game.winner.name}")
                else:
                    ui.show_message("游戏结束! 平局!")
        
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            running = False
        except Exception as e:
            ui.show_error(f"发生错误: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()

