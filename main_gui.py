"""
GUI主程序入口
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
    from ui.gui_ui import GUIUI
except ImportError:
    # 如果相对导入失败，尝试绝对导入（从项目根目录运行）
    try:
        from go_gobang_player.controller.game_controller import GameController
        from go_gobang_player.ui.gui_ui import GUIUI
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保在正确的目录下运行程序")
        sys.exit(1)


def main():
    """主函数"""
    controller = GameController()
    ui = GUIUI(controller)
    ui.run()


if __name__ == "__main__":
    main()

