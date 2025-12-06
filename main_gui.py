"""
GUI 主程序入口
"""
import sys
import os
from pathlib import Path

# 兼容直接执行 python main_gui.py：确保包可见并设置包名
if __package__ in (None, ""):
    current_dir = Path(__file__).resolve().parent
    parent_dir = current_dir.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    __package__ = current_dir.name

try:
    from .controller.game_controller import GameController
    from .ui.gui_ui import GUIUI
except ImportError as e:
    print(f"导入错误: {e}")
    sys.exit(1)


def main():
    controller = GameController()
    ui = GUIUI(controller)
    ui.run()


if __name__ == "__main__":
    main()
