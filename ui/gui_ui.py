"""
图形界面 UI（tkinter）
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from typing import Optional
from ..core.game import Game
from ..core.stone import Stone
from ..core.position import Position
from ..config import GameConfig


class GUIUI:
    """Tkinter 界面"""

    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("棋类对战平台")
        self.root.geometry("960x820")

        # 棋盘相关
        self.canvas: Optional[tk.Canvas] = None
        self.cell_size = 32
        self.board_padding = 60
        self.stone_radius = 12

        # 状态
        self.current_game: Optional[Game] = None
        self.click_enabled = False

        self._create_menu()
        self._create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    # ---------- UI 构建 ----------
    def _create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="游戏", menu=game_menu)
        game_menu.add_command(label="新游戏", command=self._show_new_game_dialog)
        game_menu.add_command(label="重新开始", command=self._restart_game)
        game_menu.add_separator()
        game_menu.add_command(label="保存", command=self._save_game)
        game_menu.add_command(label="加载", command=self._load_game)
        game_menu.add_command(label="回放", command=self._replay_game)
        game_menu.add_separator()
        game_menu.add_command(label="退出", command=self._on_closing)

        account_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="账号", menu=account_menu)
        account_menu.add_command(label="注册", command=self._register_user)
        account_menu.add_command(label="登录", command=self._login_user)
        account_menu.add_command(label="查看历史", command=self._show_history)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self._show_about)

    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 信息
        info_frame = ttk.LabelFrame(main_frame, text="对局信息", padding="10")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        info_frame.columnconfigure(1, weight=1)

        self.info_label = ttk.Label(info_frame, text="请开始新游戏", font=("Arial", 12))
        self.info_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)

        self.players_label = ttk.Label(info_frame, text="", font=("Arial", 10))
        self.players_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(4, 0))

        self.status_label = ttk.Label(info_frame, text="", font=("Arial", 10), foreground="#555")
        self.status_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(4, 0))

        # 棋盘
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        self.canvas = tk.Canvas(canvas_frame, bg="#DEB887", cursor="hand2")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # 控制按钮
        button_frame = ttk.Frame(main_frame, padding="10")
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        ttk.Button(button_frame, text="新游戏", command=self._show_new_game_dialog).pack(side=tk.LEFT, padx=5)
        self.undo_button = ttk.Button(button_frame, text="悔棋", command=self._undo_move)
        self.undo_button.pack(side=tk.LEFT, padx=5)
        self.resign_button = ttk.Button(button_frame, text="认负", command=self._resign)
        self.resign_button.pack(side=tk.LEFT, padx=5)
        self.pass_button = ttk.Button(button_frame, text="虚着/跳过", command=self._pass_move)
        self.pass_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存", command=self._save_game).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="加载", command=self._load_game).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="回放", command=self._replay_game).pack(side=tk.LEFT, padx=5)

    # ---------- 对局流程 ----------
    def _show_new_game_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("新游戏")
        dialog.geometry("420x380")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="游戏类型:").grid(row=0, column=0, padx=10, pady=8, sticky=tk.W)
        game_type_var = tk.StringVar(value="gobang")
        ttk.Radiobutton(dialog, text="五子棋", variable=game_type_var, value="gobang").grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(dialog, text="围棋", variable=game_type_var, value="go").grid(row=0, column=2, sticky=tk.W)
        ttk.Radiobutton(dialog, text="黑白棋", variable=game_type_var, value="reversi").grid(row=0, column=3, sticky=tk.W)

        ttk.Label(dialog, text="棋盘大小:").grid(row=1, column=0, padx=10, pady=8, sticky=tk.W)
        board_size_var = tk.StringVar(value=str(GameConfig.DEFAULT_BOARD_SIZE))
        size_combo = ttk.Combobox(
            dialog,
            textvariable=board_size_var,
            values=[str(i) for i in range(GameConfig.MIN_BOARD_SIZE, GameConfig.MAX_BOARD_SIZE + 1)],
            width=8,
        )
        size_combo.grid(row=1, column=1, sticky=tk.W)

        def sync_size(*args):
            board_size_var.set(str(GameConfig.default_size_for(game_type_var.get())))
        game_type_var.trace_add("write", sync_size)
        sync_size()

        ttk.Label(dialog, text="模式:").grid(row=2, column=0, padx=10, pady=8, sticky=tk.W)
        mode_var = tk.StringVar(value="human")
        ttk.Radiobutton(dialog, text="本地双人", variable=mode_var, value="human").grid(row=2, column=1, sticky=tk.W)
        ttk.Radiobutton(dialog, text="人机", variable=mode_var, value="ai").grid(row=2, column=2, sticky=tk.W)
        ttk.Radiobutton(dialog, text="AI vs AI", variable=mode_var, value="aivsai").grid(row=2, column=3, sticky=tk.W)

        ttk.Label(dialog, text="人类执色(人机):").grid(row=3, column=0, padx=10, pady=8, sticky=tk.W)
        color_var = tk.StringVar(value="black")
        ttk.Radiobutton(dialog, text="黑", variable=color_var, value="black").grid(row=3, column=1, sticky=tk.W)
        ttk.Radiobutton(dialog, text="白", variable=color_var, value="white").grid(row=3, column=2, sticky=tk.W)

        ttk.Label(dialog, text="AI等级(Lv1随机 / Lv2邻近):").grid(row=4, column=0, padx=10, pady=8, sticky=tk.W)
        ai_level_var = tk.StringVar(value="2")
        ttk.Combobox(dialog, textvariable=ai_level_var, values=["1", "2"], width=6).grid(row=4, column=1, sticky=tk.W)

        ttk.Label(dialog, text="AI2等级(AI vs AI):").grid(row=5, column=0, padx=10, pady=8, sticky=tk.W)
        ai2_level_var = tk.StringVar(value="2")
        ttk.Combobox(dialog, textvariable=ai2_level_var, values=["1", "2"], width=6).grid(row=5, column=1, sticky=tk.W)

        def start_game():
            try:
                game_type = game_type_var.get()
                size = int(board_size_var.get())
                mode = mode_var.get()
                human_color = color_var.get() if mode == "ai" else None
                ai_level = int(ai_level_var.get())
                ai2_level = int(ai2_level_var.get())
                result = self.controller.start_game(game_type, size, mode, human_color, ai_level, ai2_level)
                if "失败" in result:
                    messagebox.showerror("错误", result)
                else:
                    dialog.destroy()
                    self._update_display()
                    self._maybe_run_ai()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的棋盘大小")

        ttk.Button(dialog, text="开始", command=start_game).grid(row=6, column=1, pady=12)
        ttk.Button(dialog, text="取消", command=dialog.destroy).grid(row=6, column=2, pady=12)

    def _on_canvas_click(self, event):
        if not self.click_enabled or not self.current_game or self.current_game.game_over:
            return
        if self.controller.is_ai_turn():
            return

        x = event.x - self.board_padding
        y = event.y - self.board_padding
        if x < 0 or y < 0:
            return
        col = round(x / self.cell_size)
        row = round(y / self.cell_size)
        if row < 0 or col < 0 or not self.current_game.board.is_valid_position(Position(row, col)):
            return

        message = self.controller.place_stone(Position(row, col))
        self._update_display(extra_message=message)
        self._maybe_run_ai()

    def _on_canvas_resize(self, event):
        self._update_display()

    # ---------- 控制按钮回调 ----------
    def _undo_move(self):
        message = self.controller.undo_move()
        self._update_display(extra_message=message)

    def _resign(self):
        message = self.controller.resign()
        self._update_display(extra_message=message)

    def _pass_move(self):
        message = self.controller.pass_move()
        self._update_display(extra_message=message)
        self._maybe_run_ai()

    def _save_game(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON 文件", "*.json")])
        if filename:
            message = self.controller.save_game(filename)
            messagebox.showinfo("保存", message)

    def _load_game(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON 文件", "*.json")])
        if filename:
            message = self.controller.load_game(filename)
            self._update_display(extra_message=message)
            self._maybe_run_ai()

    def _replay_game(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON 文件", "*.json")])
        if not filename:
            return
        content = self.controller.replay_game(filename)
        replay_window = tk.Toplevel(self.root)
        replay_window.title("回放")
        text = tk.Text(replay_window, wrap="none")
        text.insert(tk.END, content)
        text.config(state=tk.DISABLED)
        text.pack(fill=tk.BOTH, expand=True)

    def _restart_game(self):
        message = self.controller.restart_game()
        self._update_display(extra_message=message)
        self._maybe_run_ai()

    def _register_user(self):
        username = simpledialog.askstring("注册", "输入用户名:")
        if not username:
            return
        password = simpledialog.askstring("注册", "输入密码:", show="*")
        if password is None:
            return
        result = self.controller.register_account(username, password)
        if "失败" in result:
            messagebox.showerror("注册失败", result)
        else:
            messagebox.showinfo("注册", result)
            self._update_display()

    def _login_user(self):
        username = simpledialog.askstring("登录", "输入用户名:")
        if not username:
            return
        password = simpledialog.askstring("登录", "输入密码:", show="*")
        if password is None:
            return
        result = self.controller.login_account(username, password)
        if "失败" in result:
            if messagebox.askyesno("未找到用户", "是否注册新账号?"):
                reg_result = self.controller.register_account(username, password)
                if "失败" in reg_result:
                    messagebox.showerror("注册失败", reg_result)
                else:
                    messagebox.showinfo("注册", reg_result)
                    self._update_display()
            else:
                messagebox.showerror("登录失败", result)
        else:
            messagebox.showinfo("登录", result)
            self._update_display()

    def _show_history(self):
        history_text = self.controller.get_account_history_text()
        dialog = tk.Toplevel(self.root)
        dialog.title("对战历史")
        text = tk.Text(dialog, wrap="word", width=80, height=20)
        text.insert(tk.END, history_text)
        text.config(state=tk.DISABLED)
        text.pack(fill=tk.BOTH, expand=True)

    # ---------- 状态渲染 ----------
    def _update_display(self, extra_message: str = ""):
        self.current_game = self.controller.get_game()
        game = self.current_game
        if not game:
            self.info_label.config(text="请开始新游戏")
            self.players_label.config(text="")
            self.status_label.config(text="")
            self.canvas.delete("all")
            self.click_enabled = False
            return

        info_text = f"{game.get_game_type()} | {game.board.size}x{game.board.size}"
        if game.game_over:
            if game.winner:
                info_text += f" | 结束，获胜者: {game.winner.name}"
            else:
                info_text += " | 结束，平局"
        else:
            info_text += f" | 当前: {game.current_player.name}"
        self.info_label.config(text=info_text)

        p1_profile = self._player_profile_text(game.player1, "黑")
        p2_profile = self._player_profile_text(game.player2, "白")
        self.players_label.config(text=f"黑方: {p1_profile}\n白方: {p2_profile}")

        self._draw_board()
        self.click_enabled = not game.game_over and not self.controller.is_ai_turn()

        if extra_message:
            self.status_label.config(text=extra_message)
        else:
            self.status_label.config(text="")

    def _draw_board(self):
        game = self.current_game
        if not game:
            return
        board = game.board
        size = board.size
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        self.canvas.delete("all")

        # 重新调整单元格大小（保持方格）
        usable_w = max(width - 2 * self.board_padding, 100)
        usable_h = max(height - 2 * self.board_padding, 100)
        self.cell_size = min(usable_w, usable_h) / max(1, size - 1 if size > 1 else 1)

        # 绘制网格
        for i in range(size):
            x0 = self.board_padding
            x1 = self.board_padding + self.cell_size * (size - 1)
            y = self.board_padding + i * self.cell_size
            self.canvas.create_line(x0, y, x1, y, fill="#8B4513")
            self.canvas.create_line(
                self.board_padding + i * self.cell_size,
                self.board_padding,
                self.board_padding + i * self.cell_size,
                self.board_padding + self.cell_size * (size - 1),
                fill="#8B4513",
            )

        # 绘制棋子
        for r in range(size):
            for c in range(size):
                stone = board.get_stone(Position(r, c))
                if stone == Stone.EMPTY:
                    continue
                x = self.board_padding + c * self.cell_size
                y = self.board_padding + r * self.cell_size
                self.canvas.create_oval(
                    x - self.stone_radius,
                    y - self.stone_radius,
                    x + self.stone_radius,
                    y + self.stone_radius,
                    fill="black" if stone == Stone.BLACK else "white",
                    outline="black",
                )

    def _player_profile_text(self, player, color_text: str) -> str:
        profile = getattr(player, "profile", {}) or {}
        role = ""
        if profile.get("is_ai"):
            role = f"AI Lv{profile.get('ai_level', '')}"
        elif profile.get("is_guest"):
            role = "游客"
        else:
            role = profile.get("username", player.name)
        stats = profile.get("stats", {})
        stats_str = f"(战绩 {stats.get('wins',0)}/{stats.get('games',0)})" if stats else ""
        return f"{player.name} [{role}] {stats_str}"

    def _maybe_run_ai(self):
        game = self.controller.get_game()
        if not game or game.game_over:
            return
        while self.controller.is_ai_turn() and not game.game_over:
            message = self.controller.make_ai_move()
            self._update_display(extra_message=message)
            game = self.controller.get_game()

    def _on_closing(self):
        self.root.destroy()

    def _show_about(self):
        messagebox.showinfo("关于", "棋类对战平台\n支持五子棋、围棋、黑白棋\n人机/双人/AI对战，支持录像回放与账号战绩")

    def run(self):
        self.root.mainloop()
