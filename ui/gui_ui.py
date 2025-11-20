"""
图形界面UI（使用tkinter）
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from typing import Optional, Callable
from ..core.game import Game
from ..core.board import Board
from ..core.stone import Stone
from ..core.position import Position
from ..config import GameConfig


class GUIUI:
    """图形界面"""
    
    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("棋类对战平台")
        self.root.geometry("800x700")
        
        # 棋盘相关
        self.canvas: Optional[tk.Canvas] = None
        self.cell_size = 30
        self.board_padding = 50
        self.stone_radius = 12
        
        # 游戏状态
        self.current_game: Optional[Game] = None
        self.board_size = 15
        self.click_enabled = False
        
        # 创建界面
        self._create_menu()
        self._create_widgets()
        
        # 绑定事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 游戏菜单
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="游戏", menu=game_menu)
        game_menu.add_command(label="新游戏", command=self._show_new_game_dialog)
        game_menu.add_command(label="重新开始", command=self._restart_game)
        game_menu.add_separator()
        game_menu.add_command(label="保存游戏", command=self._save_game)
        game_menu.add_command(label="加载游戏", command=self._load_game)
        game_menu.add_separator()
        game_menu.add_command(label="退出", command=self._on_closing)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self._show_about)
    
    def _create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 信息面板
        info_frame = ttk.LabelFrame(main_frame, text="游戏信息", padding="10")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        self.info_label = ttk.Label(info_frame, text="请开始新游戏", font=("Arial", 12))
        self.info_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        self.status_label = ttk.Label(info_frame, text="", font=("Arial", 10))
        self.status_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # 棋盘画布
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.canvas = tk.Canvas(canvas_frame, bg="#DEB887", cursor="hand2")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        
        # 控制按钮面板
        button_frame = ttk.Frame(main_frame, padding="10")
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(button_frame, text="新游戏", command=self._show_new_game_dialog).pack(side=tk.LEFT, padx=5)
        self.undo_button = ttk.Button(button_frame, text="悔棋", command=self._undo_move)
        self.undo_button.pack(side=tk.LEFT, padx=5)
        self.resign_button = ttk.Button(button_frame, text="认负", command=self._resign)
        self.resign_button.pack(side=tk.LEFT, padx=5)
        self.pass_button = ttk.Button(button_frame, text="虚着", command=self._pass_move)
        self.pass_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存", command=self._save_game).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="加载", command=self._load_game).pack(side=tk.LEFT, padx=5)
    
    def _show_new_game_dialog(self):
        """显示新游戏对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("新游戏")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 游戏类型
        ttk.Label(dialog, text="游戏类型:", font=("Arial", 10)).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        game_type_var = tk.StringVar(value="gobang")
        game_type_frame = ttk.Frame(dialog)
        game_type_frame.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
        ttk.Radiobutton(game_type_frame, text="五子棋", variable=game_type_var, value="gobang").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(game_type_frame, text="围棋", variable=game_type_var, value="go").pack(side=tk.LEFT, padx=5)
        
        # 棋盘大小
        ttk.Label(dialog, text="棋盘大小:", font=("Arial", 10)).grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        board_size_var = tk.StringVar(value="15")
        board_size_combo = ttk.Combobox(dialog, textvariable=board_size_var, 
                                        values=[str(i) for i in range(GameConfig.MIN_BOARD_SIZE, GameConfig.MAX_BOARD_SIZE + 1)],
                                        state="readonly", width=10)
        board_size_combo.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        
        # 对战模式
        ttk.Label(dialog, text="对战模式:", font=("Arial", 10)).grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        mode_var = tk.StringVar(value="human")
        mode_frame = ttk.Frame(dialog)
        mode_frame.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)
        ttk.Radiobutton(mode_frame, text="双人对战", variable=mode_var, value="human").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="人机对战", variable=mode_var, value="ai").pack(side=tk.LEFT, padx=5)
        
        # 颜色选择（仅人机对战）
        ttk.Label(dialog, text="执子颜色:", font=("Arial", 10)).grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        color_var = tk.StringVar(value="black")
        color_frame = ttk.Frame(dialog)
        color_frame.grid(row=3, column=1, padx=10, pady=10, sticky=tk.W)
        ttk.Radiobutton(color_frame, text="黑", variable=color_var, value="black").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(color_frame, text="白", variable=color_var, value="white").pack(side=tk.LEFT, padx=5)
        
        def update_color_state(*args):
            """根据模式更新颜色选择状态"""
            if mode_var.get() == "human":
                for widget in color_frame.winfo_children():
                    widget.config(state=tk.DISABLED)
            else:
                for widget in color_frame.winfo_children():
                    widget.config(state=tk.NORMAL)
        
        mode_var.trace("w", update_color_state)
        update_color_state()
        
        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        def start_game():
            try:
                game_type = game_type_var.get()
                board_size = int(board_size_var.get())
                mode = mode_var.get()
                color = color_var.get() if mode == "ai" else None
                
                result = self.controller.start_game(game_type, board_size, mode, color)
                if "失败" in result:
                    messagebox.showerror("错误", result)
                else:
                    dialog.destroy()
                    self._update_display()
                    self._check_ai_turn()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的棋盘大小")
        
        ttk.Button(button_frame, text="开始", command=start_game).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=10)
    
    def _on_canvas_click(self, event):
        """处理棋盘点击事件"""
        if not self.click_enabled or not self.current_game or self.current_game.game_over:
            return
        
        # 检查是否是AI回合，AI回合时不允许玩家点击落子
        if self.controller.is_ai_turn():
            return
        
        # 计算点击的格子位置
        x = event.x - self.board_padding
        y = event.y - self.board_padding
        
        if x < 0 or y < 0:
            return
        
        col = round(x / self.cell_size)
        row = round(y / self.cell_size)
        
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            position = Position(row, col)
            result = self.controller.place_stone(position)
            
            if "成功" in result or "结束" in result:
                self._update_display()
                # 延迟检查AI回合，确保界面已更新
                self.root.after(100, self._check_ai_turn)
                
                if self.current_game and self.current_game.game_over:
                    self.root.after(200, self._show_game_over)
            else:
                messagebox.showwarning("无效操作", result)
    
    def _on_canvas_resize(self, event):
        """处理画布大小变化"""
        if self.current_game:
            self._draw_board()
    
    def _draw_board(self):
        """绘制棋盘"""
        if not self.canvas or not self.current_game:
            return
        
        self.canvas.delete("all")
        
        # 计算棋盘大小和位置
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        board_pixel_size = min(canvas_width, canvas_height) - 2 * self.board_padding
        self.cell_size = board_pixel_size / (self.board_size - 1) if self.board_size > 1 else board_pixel_size
        
        # 调整padding使棋盘居中
        self.board_padding = (min(canvas_width, canvas_height) - board_pixel_size) / 2
        
        # 绘制网格线
        for i in range(self.board_size):
            # 横线
            y = self.board_padding + i * self.cell_size
            self.canvas.create_line(
                self.board_padding, y,
                self.board_padding + (self.board_size - 1) * self.cell_size, y,
                fill="black", width=1
            )
            # 竖线
            x = self.board_padding + i * self.cell_size
            self.canvas.create_line(
                x, self.board_padding,
                x, self.board_padding + (self.board_size - 1) * self.cell_size,
                fill="black", width=1
            )
        
        # 绘制星位（围棋19路棋盘和15路棋盘）
        if self.board_size == 19:
            star_positions = [(3, 3), (3, 9), (3, 15), (9, 3), (9, 9), (9, 15), (15, 3), (15, 9), (15, 15)]
            for row, col in star_positions:
                x = self.board_padding + col * self.cell_size
                y = self.board_padding + row * self.cell_size
                self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="black")
        elif self.board_size == 15:
            star_positions = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
            for row, col in star_positions:
                x = self.board_padding + col * self.cell_size
                y = self.board_padding + row * self.cell_size
                self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="black")
        
        # 绘制棋子
        for row in range(self.board_size):
            for col in range(self.board_size):
                position = Position(row, col)
                stone = self.current_game.board.get_stone(position)
                if stone != Stone.EMPTY:
                    self._draw_stone(row, col, stone)
    
    def _draw_stone(self, row: int, col: int, stone: Stone):
        """绘制棋子"""
        x = self.board_padding + col * self.cell_size
        y = self.board_padding + row * self.cell_size
        
        if stone == Stone.BLACK:
            self.canvas.create_oval(
                x - self.stone_radius, y - self.stone_radius,
                x + self.stone_radius, y + self.stone_radius,
                fill="black", outline="black", width=2
            )
        elif stone == Stone.WHITE:
            self.canvas.create_oval(
                x - self.stone_radius, y - self.stone_radius,
                x + self.stone_radius, y + self.stone_radius,
                fill="white", outline="black", width=2
            )
    
    def _update_display(self):
        """更新显示"""
        self.current_game = self.controller.get_game()
        
        if self.current_game:
            self.board_size = self.current_game.board.size
            
            # 更新信息
            game_type_name = "五子棋" if self.current_game.get_game_type() == "gobang" else "围棋"
            current_player_name = self.current_game.current_player.name
            current_color = "黑" if self.current_game.current_player.color == Stone.BLACK else "白"
            
            info_text = f"游戏类型: {game_type_name} | 棋盘大小: {self.board_size}x{self.board_size}"
            status_text = f"当前玩家: {current_player_name} ({current_color})"
            
            # 检查是否是AI回合
            is_ai_turn = self.controller.is_ai_turn()
            
            # 设置点击启用状态：只有非AI回合且游戏未结束时才能点击
            self.click_enabled = not self.current_game.game_over and not is_ai_turn
            
            # 更新按钮状态：AI回合时禁用所有玩家操作按钮
            if self.current_game.game_over:
                # 游戏结束时禁用所有操作按钮
                self.click_enabled = False
                self.undo_button.config(state=tk.DISABLED)
                self.resign_button.config(state=tk.DISABLED)
                self.pass_button.config(state=tk.DISABLED)
                if self.current_game.winner:
                    status_text = f"游戏结束! 获胜者: {self.current_game.winner.name}"
                else:
                    status_text = "游戏结束! 平局!"
            elif is_ai_turn:
                # AI回合时禁用所有玩家操作按钮
                self.undo_button.config(state=tk.DISABLED)
                self.resign_button.config(state=tk.DISABLED)
                self.pass_button.config(state=tk.DISABLED)
            else:
                # 玩家回合时启用相关按钮
                self.undo_button.config(state=tk.NORMAL)
                self.resign_button.config(state=tk.NORMAL)
                # 虚着按钮只在围棋时启用
                if self.current_game.get_game_type() == "go":
                    self.pass_button.config(state=tk.NORMAL)
                else:
                    self.pass_button.config(state=tk.DISABLED)
        else:
            info_text = "请开始新游戏"
            status_text = ""
            self.click_enabled = False
            self.undo_button.config(state=tk.NORMAL)
            self.resign_button.config(state=tk.NORMAL)
            self.pass_button.config(state=tk.NORMAL)
        
        self.info_label.config(text=info_text)
        self.status_label.config(text=status_text)
        
        # 重绘棋盘
        self._draw_board()
    
    def _check_ai_turn(self):
        """检查并执行AI回合"""
        if self.controller.is_ai_turn() and self.current_game and not self.current_game.game_over:
            # 延迟执行，让界面先更新
            self.root.after(500, self._execute_ai_move)
    
    def _execute_ai_move(self):
        """执行AI落子"""
        if self.controller.is_ai_turn() and self.current_game and not self.current_game.game_over:
            result = self.controller.make_ai_move()
            self._update_display()
            
            if self.current_game and self.current_game.game_over:
                self._show_game_over()
    
    def _undo_move(self):
        """悔棋"""
        if not self.current_game:
            messagebox.showwarning("提示", "请先开始游戏")
            return
        
        result = self.controller.undo_move()
        if "成功" in result:
            self._update_display()
        else:
            messagebox.showwarning("提示", result)
    
    def _resign(self):
        """投子认负"""
        if not self.current_game:
            messagebox.showwarning("提示", "请先开始游戏")
            return
        
        if messagebox.askyesno("确认", "确定要投子认负吗？"):
            result = self.controller.resign()
            self._update_display()
            self._show_game_over()
            messagebox.showinfo("游戏结束", result)
    
    def _pass_move(self):
        """虚着（仅围棋）"""
        if not self.current_game:
            messagebox.showwarning("提示", "请先开始游戏")
            return
        
        if self.current_game.get_game_type() != "go":
            messagebox.showwarning("提示", "只有围棋支持虚着")
            return
        
        result = self.controller.pass_move()
        if "成功" in result or "结束" in result:
            self._update_display()
            self._check_ai_turn()
            if self.current_game and self.current_game.game_over:
                self._show_game_over()
        else:
            messagebox.showwarning("提示", result)
    
    def _save_game(self):
        """保存游戏"""
        if not self.current_game:
            messagebox.showwarning("提示", "没有正在进行的游戏")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            result = self.controller.save_game(filename)
            if "成功" in result or "保存" in result:
                messagebox.showinfo("成功", result)
            else:
                messagebox.showerror("错误", result)
    
    def _load_game(self):
        """加载游戏"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            result = self.controller.load_game(filename)
            if "成功" in result or "加载" in result:
                self._update_display()
                messagebox.showinfo("成功", result)
            else:
                messagebox.showerror("错误", result)
    
    def _restart_game(self):
        """重新开始游戏"""
        if not self.current_game:
            messagebox.showwarning("提示", "没有正在进行的游戏")
            return
        
        if messagebox.askyesno("确认", "确定要重新开始游戏吗？"):
            result = self.controller.restart_game()
            self._update_display()
            self._check_ai_turn()
    
    def _show_game_over(self):
        """显示游戏结束消息"""
        if self.current_game and self.current_game.game_over:
            if self.current_game.winner:
                messagebox.showinfo("游戏结束", f"游戏结束!\n获胜者: {self.current_game.winner.name}")
            else:
                messagebox.showinfo("游戏结束", "游戏结束!\n平局!")
    
    def _show_about(self):
        """显示关于对话框"""
        about_text = """棋类对战平台 v1.0

支持五子棋和围棋的对战
支持人机对战和本地双人对战

功能特性:
- 五子棋和围棋完整规则
- 超级AI对战
- 悔棋、保存、加载等功能
- 图形化界面

使用Python + tkinter开发"""
        messagebox.showinfo("关于", about_text)
    
    def _on_closing(self):
        """关闭窗口"""
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            self.root.destroy()
    
    def run(self):
        """运行GUI"""
        self._update_display()
        self.root.mainloop()

