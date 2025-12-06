"""
游戏控制器：负责玩家创建、AI 回合、存档、回放、账号管理
"""
from typing import Optional, List
from ..core.game import Game
from ..core.game_factory import GameFactory
from ..core.player import Player
from ..core.human_player import HumanPlayer
from ..core.ai_player import SuperAI, RandomAI, AIPlayer
from ..core.stone import Stone
from ..core.position import Position
from ..persistence.file_manager import FileManager
from ..persistence.account_manager import AccountManager
from ..config import GameConfig
from ..exceptions import (
    InvalidMoveException, GameOverException, NoHistoryException,
    FileOperationException, InvalidInputException
)


class GameController:
    """游戏控制器"""

    def __init__(self):
        self.game: Optional[Game] = None
        self.file_manager = FileManager()
        self.account_manager = AccountManager()
        self.logged_accounts = {"black": None, "white": None}
        self.active_account = None  # 当前登录的用户
        self.ai_players: List[AIPlayer] = []
        self.last_setup = {}

    # ------------- 账号相关 -------------
    def register_account(self, username: str, password: str) -> str:
        if self.game and not self.game.game_over:
            return "对局进行中，无法注册或登录"
        try:
            profile = self.account_manager.register(username, password)
            profile["is_guest"] = False
            self.active_account = profile
            return f"注册成功，当前用户: {profile['username']}"
        except FileOperationException as e:
            return f"注册失败: {e}"

    def login_account(self, username: str, password: str, color: str = "black") -> str:
        # color 参数仅为兼容旧调用，实际仅支持单用户登录
        if self.game and not self.game.game_over:
            return "对局进行中，无法注册或登录"
        try:
            profile = self.account_manager.login(username, password)
            profile["is_guest"] = False
            self.active_account = profile
            # 兼容旧逻辑：同时写入两侧，避免其它地方取不到
            self.logged_accounts["black"] = profile
            self.logged_accounts["white"] = profile
            return f"登录成功，当前用户: {username}"
        except FileOperationException as e:
            return f"登录失败: {e}"

    # ------------- 开局与玩家创建 -------------
    def start_game(
        self,
        game_type: str,
        board_size: int,
        mode: str,
        human_color: Optional[str] = None,
        ai_level: int = 2,
        ai2_level: Optional[int] = None,
    ) -> str:
        """开始游戏"""
        try:
            size = board_size or GameConfig.default_size_for(game_type)
            mode = mode.lower()
            self.ai_players = []

            if mode == "human":
                black = self._build_human(Stone.BLACK, use_active=True)
                white = self._build_human(Stone.WHITE, use_active=False)
            elif mode == "ai":
                human_color = "black" if human_color is None else human_color.lower()
                human_is_black = human_color == "black"
                human = self._build_human(Stone.BLACK if human_is_black else Stone.WHITE)
                ai_player = self._create_ai(ai_level, Stone.WHITE if human_is_black else Stone.BLACK)
                if human_is_black:
                    black, white = human, ai_player
                else:
                    black, white = ai_player, human
            elif mode == "aivsai":
                ai1 = self._create_ai(ai_level, Stone.BLACK)
                ai2 = self._create_ai(ai2_level or ai_level, Stone.WHITE)
                black, white = ai1, ai2
            else:
                return "模式必须是 human / ai / aivsai"

            self.ai_players = [p for p in [black, white] if isinstance(p, AIPlayer)]
            self.game = GameFactory.create_game(game_type, size, black, white)
            self.last_setup = {
                "game_type": game_type,
                "board_size": size,
                "mode": mode,
                "human_color": human_color,
                "ai_level": ai_level,
                "ai2_level": ai2_level or ai_level,
            }

            return f"游戏已开始: {game_type} {size}x{size} 模式 {mode}"
        except Exception as e:
            return f"开始游戏失败: {str(e)}"

    def _build_human(self, color: Stone, use_active: bool = True) -> HumanPlayer:
        # 当前登录用户走人类位，否则使用游客身份
        if use_active and self.active_account:
            profile = {
                "username": self.active_account.get("username"),
                "stats": self.active_account.get("stats", {}),
                "is_guest": False,
            }
            name = self.active_account.get("username", "玩家")
        else:
            profile = {"username": "游客", "is_guest": True}
            name = "黑方" if color == Stone.BLACK else "白方"
        return HumanPlayer(color, name=name, profile=profile)

    def _create_ai(self, level: int, color: Stone) -> AIPlayer:
        level = level or 2
        profile = {"is_ai": True, "ai_level": level, "username": f"AI-Lv{level}"}
        if level == 1:
            return RandomAI(color, name=f"AI-Lv1", profile=profile)
        return SuperAI(color, name=f"AI-Lv2", profile=profile)

    def _color_key(self, color: str) -> Optional[str]:
        if color.lower() in ["black", "b"]:
            return "black"
        if color.lower() in ["white", "w"]:
            return "white"
        return None

    # ------------- 行棋操作 -------------
    def place_stone(self, position: Position) -> str:
        """落子（玩家）"""
        if not self.game:
            return "请先开始游戏"
        if self.is_ai_turn():
            return "AI回合进行中，等待AI落子"

        mover = self.game.current_player
        try:
            result = self.game.make_move(position)
            self._notify_ai_after_move(mover.color, position)
            message = f"落子成功: {position}"
            if getattr(self.game, "forced_pass_message", None):
                message += f" | {self.game.forced_pass_message}"
            if not result:
                self._update_stats_on_end()
                if self.game.winner:
                    message = f"游戏结束! {self.game.winner.name} 获胜!"
                else:
                    message = "游戏结束! 平局!"
            return message
        except InvalidMoveException as e:
            return f"无效落子: {str(e)}"
        except GameOverException as e:
            return f"游戏已结束: {str(e)}"
        except Exception as e:
            return f"落子失败: {str(e)}"

    def pass_move(self) -> str:
        """虚着/跳过"""
        if not self.game:
            return "请先开始游戏"
        if self.is_ai_turn():
            return "AI回合不能虚着"
        try:
            result = self.game.make_move(None)
            message = "虚着成功"
            if getattr(self.game, "forced_pass_message", None):
                message = self.game.forced_pass_message
            if not result:
                self._update_stats_on_end()
                if self.game.winner:
                    message = f"游戏结束! {self.game.winner.name} 获胜!"
                else:
                    message = "游戏结束! 平局!"
            return message
        except InvalidMoveException as e:
            return f"无效操作: {str(e)}"
        except Exception as e:
            return f"虚着失败: {str(e)}"

    def undo_move(self) -> str:
        """悔棋（撤销自己和对手各一步）"""
        if not self.game:
            return "请先开始游戏"
        if self.is_ai_turn():
            return "AI回合不能悔棋，请等待AI落子"
        try:
            if self.game.can_undo_two():
                self.game.undo_two()
                return "悔棋成功（已撤销两步）"
            elif self.game.can_undo():
                self.game.undo()
                return "悔棋成功（已撤销一步）"
            else:
                return "悔棋失败: 没有可悔的棋"
        except NoHistoryException as e:
            return f"悔棋失败: {str(e)}"
        except Exception as e:
            return f"悔棋失败: {str(e)}"

    def resign(self) -> str:
        """投子认负"""
        if not self.game:
            return "请先开始游戏"
        if self.is_ai_turn():
            return "AI不能认负"
        try:
            loser = self.game.current_player
            self.game.resign(loser)
            self._update_stats_on_end()
            return f"{loser.name} 投子认负! {self.game.winner.name} 获胜!"
        except Exception as e:
            return f"认负失败: {str(e)}"

    # ------------- 存档 / 读档 / 回放 -------------
    def save_game(self, filename: str) -> str:
        """保存游戏"""
        if not self.game:
            return "没有正在进行的游戏"
        try:
            game_state = self.game.get_state_dict()
            self.file_manager.save_game(game_state, filename)
            return f"游戏已保存到: {filename}"
        except FileOperationException as e:
            return f"保存失败: {str(e)}"
        except Exception as e:
            return f"保存失败: {str(e)}"

    def load_game(self, filename: str) -> str:
        """加载游戏"""
        try:
            game_state = self.file_manager.load_game(filename)
            player1 = self._player_from_state(
                Stone(game_state['player1_color']),
                game_state.get('player1_name', ''),
                game_state.get('player1_profile', {})
            )
            player2 = self._player_from_state(
                Stone(game_state['player2_color']),
                game_state.get('player2_name', ''),
                game_state.get('player2_profile', {})
            )
            self.game = GameFactory.create_game(
                game_state['game_type'],
                game_state['board_size'],
                player1,
                player2
            )
            self.game.load_state_dict(game_state)
            self.ai_players = [p for p in [player1, player2] if isinstance(p, AIPlayer)]
            self.last_setup = {
                "game_type": game_state['game_type'],
                "board_size": game_state['board_size'],
                "mode": self._infer_mode_from_players(player1, player2),
                "human_color": "black" if isinstance(player1, HumanPlayer) else "white",
                "ai_level": self._ai_level(player1) or self._ai_level(player2),
                "ai2_level": self._ai_level(player2),
            }
            return f"游戏已从 {filename} 加载"
        except FileOperationException as e:
            return f"加载失败: {str(e)}"
        except Exception as e:
            return f"加载失败: {str(e)}"

    def replay_game(self, filename: str) -> str:
        """读取存档并生成简单的文字回放"""
        try:
            state = self.file_manager.load_game(filename)
            moves = state.get("moves_log", [])
            if not moves:
                return "存档中没有录像记录"

            replay = GameFactory.create_game(
                state["game_type"],
                state["board_size"],
                self._player_from_state(Stone(state["player1_color"]), state.get("player1_name", ""), state.get("player1_profile", {})),
                self._player_from_state(Stone(state["player2_color"]), state.get("player2_name", ""), state.get("player2_profile", {})),
            )
            frames = [self._board_to_text(replay.board, header="初始局面")]
            step = 0
            for mv in moves:
                step += 1
                pos = mv.get("position")
                try:
                    if pos:
                        replay.make_move(Position(pos[0], pos[1]))
                    else:
                        replay.make_move(None)
                except Exception as e:
                    frames.append(f"第{step}步回放失败: {e}")
                    break
                label = f"第{step}步 {mv.get('player_name')} -> {pos if pos else 'pass'}"
                frames.append(self._board_to_text(replay.board, header=label))
            return "\n\n".join(frames)
        except FileOperationException as e:
            return f"回放失败: {e}"
        except Exception as e:
            return f"回放失败: {e}"

    # ------------- 其他辅助 -------------
    def restart_game(self) -> str:
        """重新开始游戏"""
        if not self.game:
            return "没有正在进行的游戏"
        setup = self.last_setup or {}
        return self.start_game(
            setup.get("game_type", self.game.get_game_type()),
            setup.get("board_size", self.game.board.size),
            setup.get("mode", "human"),
            setup.get("human_color"),
            setup.get("ai_level", 2),
            setup.get("ai2_level", 2),
        )

    def get_game(self) -> Optional[Game]:
        return self.game

    def is_ai_turn(self) -> bool:
        return self.game is not None and any(self.game.current_player == ai for ai in self.ai_players)

    def make_ai_move(self) -> str:
        """执行当前 AI 的落子"""
        if not self.is_ai_turn():
            return "不是AI回合"
        ai_player = next(ai for ai in self.ai_players if self.game.current_player == ai)
        mover = self.game.current_player
        try:
            position = ai_player.make_move(self.game)
            result = self.game.make_move(position)
            self._notify_ai_after_move(mover.color, position)
            message = f"{ai_player.name} 落子: {position}"
            if getattr(self.game, "forced_pass_message", None):
                message += f" | {self.game.forced_pass_message}"
            if not result:
                self._update_stats_on_end()
                if self.game.winner:
                    message = f"游戏结束! {self.game.winner.name} 获胜!"
                else:
                    message = "游戏结束! 平局!"
            return message
        except Exception as e:
            return f"AI落子失败: {str(e)}"

    def _notify_ai_after_move(self, mover_color: Stone, position: Position):
        for ai in self.ai_players:
            if ai.color != mover_color and hasattr(ai, "update_opponent_move"):
                try:
                    ai.update_opponent_move(position)
                except Exception:
                    pass

    def _update_stats_on_end(self):
        """对局结束后更新账号战绩和历史（仅本地双人或人机对战）"""
        if not self.game or not self.game.game_over or not self.active_account:
            return

        game = self.game
        mode = self._infer_mode_from_players(game.player1, game.player2)
        # 仅记录本地双人/人机，不记录 AI vs AI
        if mode == "aivsai":
            return

        winner_color = game.winner.color if game.winner else None
        username = self.active_account.get("username")

        active_player = None
        for player in [game.player1, game.player2]:
            profile = getattr(player, "profile", {}) or {}
            if profile.get("username") == username:
                active_player = player
                break
        if not active_player:
            return

        win = winner_color is not None and active_player.color == winner_color
        is_draw = winner_color is None
        self.account_manager.update_stats(username, win)

        from datetime import datetime

        opponent = game.player2 if active_player == game.player1 else game.player1
        opponent_name = getattr(opponent, "name", "未知")
        self.account_manager.add_history(
            username,
            {
                "game_type": game.get_game_type(),
                "board_size": game.board.size,
                "mode": mode,
                "color": "black" if active_player.color == Stone.BLACK else "white",
                "result": "draw" if is_draw else ("win" if win else "loss"),
                "opponent": opponent_name,
                "ended_at": datetime.now().isoformat(timespec="seconds"),
            },
        )

    def _player_from_state(self, color: Stone, name: str, profile: dict) -> Player:
        profile = profile or {}
        if profile.get("is_ai"):
            level = profile.get("ai_level", 2)
            ai = self._create_ai(level, color)
            ai.name = name or ai.name
            return ai
        human = HumanPlayer(color, name=name or ("黑方" if color == Stone.BLACK else "白方"), profile=profile)
        return human

    def get_account_history_text(self) -> str:
        """返回当前用户的对战历史文本"""
        if not self.active_account:
            return "未登录，无法查看历史"
        try:
            history = self.account_manager.get_history(self.active_account["username"])
            if not history:
                return "暂无对战历史"
            lines = []
            for idx, h in enumerate(history, 1):
                lines.append(
                    f"{idx}. {h.get('ended_at','')} | {h.get('game_type','')} {h.get('board_size','')}x{h.get('board_size','')} | "
                    f"{h.get('mode','')} | {h.get('color','')} | 结果: {h.get('result','')} | 对手: {h.get('opponent','')}"
                )
            return "\n".join(lines)
        except FileOperationException as e:
            return f"读取历史失败: {e}"

    def _infer_mode_from_players(self, p1: Player, p2: Player) -> str:
        ai_count = len([p for p in [p1, p2] if isinstance(p, AIPlayer)])
        if ai_count == 2:
            return "aivsai"
        if ai_count == 1:
            return "ai"
        return "human"

    def _ai_level(self, player: Player) -> Optional[int]:
        return getattr(player, "level", None)

    def _board_to_text(self, board, header: str = "") -> str:
        """将棋盘转为文本，便于回放展示"""
        size = board.size
        lines = []
        if header:
            lines.append(header)
        header_nums = "   " + " ".join(str(i).rjust(2) for i in range(size))
        lines.append(header_nums)
        lines.append("  " + "-" * (size * 3 + 1))
        for r in range(size):
            line = str(r).rjust(2) + "|"
            for c in range(size):
                line += str(board.get_stone(Position(r, c)))
                if c < size - 1:
                    line += " "
            line += "|"
            lines.append(line)
        lines.append("  " + "-" * (size * 3 + 1))
        lines.append(header_nums)
        return "\n".join(lines)
