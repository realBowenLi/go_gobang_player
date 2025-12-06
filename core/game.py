"""
游戏抽象基类
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from .board import Board
from .player import Player
from .stone import Stone
from .position import Position
from ..exceptions import InvalidMoveException, GameOverException, NoHistoryException


class Game(ABC):
    """游戏抽象基类"""
    
    def __init__(self, board: Board, player1: Player, player2: Player):
        self.board = board
        self.player1 = player1
        self.player2 = player2
        self.current_player: Player = player1
        self.game_over = False
        self.winner: Optional[Player] = None
        self.resigned_player: Optional[Player] = None
        self.history: List[Dict[str, Any]] = []  # 历史记录（用于悔棋）
        self.last_move: Optional[Position] = None
        self.moves_log: List[Dict[str, Any]] = []  # 录像
    
    def make_move(self, position: Optional[Position] = None) -> bool:
        """
        执行落子
        position为None表示虚着（仅围棋）
        返回True表示游戏继续，False表示游戏结束
        """
        if self.game_over:
            raise GameOverException("游戏已结束")
        
        # 虚着处理（仅围棋）
        if position is None:
            if not self._supports_pass():
                raise InvalidMoveException("此游戏不支持虚着")
            # 保存当前状态（用于悔棋）
            self._save_state()
            self._record_move(self.current_player, None)
            result = self._handle_pass()
            return result
        
        # 检查落子合法性
        if not self.board.is_valid_move(position, self.current_player.color):
            raise InvalidMoveException(f"无效的落子位置: {position}")
        
        # 保存当前状态（用于悔棋）
        self._save_state()
        
        # 执行落子
        captured = self.board.place_stone(position, self.current_player.color)
        self.last_move = position
        self._record_move(self.current_player, position)
        
        # 检查游戏是否结束
        if self._check_win_condition(position):
            self.game_over = True
            self.winner = self.current_player
            return False
        
        # 检查是否平局
        if self._check_draw():
            self.game_over = True
            return False
        
        # 切换玩家
        self._switch_player()
        return True
    
    def _save_state(self):
        """保存当前状态到历史记录"""
        state = {
            'board': self.board.get_board_copy(),
            'current_player': self.current_player.color.value,
            'last_move': (self.last_move.row, self.last_move.col) if self.last_move else None
        }
        self.history.append(state)

    def _record_move(self, player: Player, position: Optional[Position]):
        """记录录像轨迹"""
        entry = {
            'player_name': player.name,
            'color': player.color.value,
            'position': (position.row, position.col) if position else None
        }
        self.moves_log.append(entry)

    def _safe_profile(self, player: Player) -> dict:
        profile = getattr(player, "profile", {}) or {}
        return {
            "username": profile.get("username"),
            "stats": profile.get("stats"),
            "is_guest": profile.get("is_guest", False),
            "is_ai": profile.get("is_ai", False),
            "ai_level": profile.get("ai_level"),
        }
    
    def undo(self):
        """悔棋一步"""
        if not self.history:
            raise NoHistoryException("没有可悔的棋")
        
        # 恢复上一个状态
        state = self.history.pop()
        self.board.set_board(state['board'])
        
        # 恢复当前玩家
        if state['current_player'] == self.player1.color.value:
            self.current_player = self.player1
        else:
            self.current_player = self.player2
        
        # 恢复上一步落子位置
        last_move_data = state.get('last_move')
        if last_move_data:
            if isinstance(last_move_data, tuple) and len(last_move_data) == 2:
                self.last_move = Position(last_move_data[0], last_move_data[1])
            elif isinstance(last_move_data, Position):
                self.last_move = last_move_data
            else:
                self.last_move = None
        else:
            self.last_move = None

        if self.moves_log:
            self.moves_log.pop()
        
        # 如果游戏已结束，恢复为未结束状态
        if self.game_over:
            self.game_over = False
            self.winner = None
            self.resigned_player = None
    
    def can_undo(self) -> bool:
        """检查是否可以悔棋"""
        return len(self.history) > 0
    
    def can_undo_two(self) -> bool:
        """检查是否可以悔棋两步"""
        return len(self.history) >= 2
    
    def undo_two(self):
        """悔棋两步（撤销自己和对手各一步）"""
        if not self.can_undo_two():
            raise NoHistoryException("没有足够的棋可以悔（需要至少两步）")
        
        # 悔棋两步
        self.undo()  # 撤销对手的落子
        self.undo()  # 撤销自己的落子
    
    def resign(self, player: Player):
        """投子认负"""
        if self.game_over:
            raise GameOverException("游戏已结束")
        if player != self.current_player:
            raise InvalidMoveException("只能当前玩家认负")
        
        # 检查是否是AI玩家，AI不能认负
        from .ai_player import SuperAI
        if isinstance(player, SuperAI):
            raise InvalidMoveException("AI不能认负")
        
        self.game_over = True
        self.resigned_player = player
        self.winner = self.player2 if player == self.player1 else self.player1
    
    def _switch_player(self):
        """切换当前玩家"""
        self.current_player = self.player2 if self.current_player == self.player1 else self.player1
    
    def get_state_dict(self) -> Dict[str, Any]:
        """获取游戏状态字典（用于保存）"""
        # 转换历史记录中的board为可序列化的格式
        serialized_history = []
        for state in self.history:
            serialized_state = {
                'board': [[stone.value if isinstance(stone, Stone) else stone for stone in row] for row in state['board']],
                'current_player': state['current_player'],
                'last_move': state.get('last_move')
            }
            serialized_history.append(serialized_state)
        
        return {
            'game_type': self.get_game_type(),
            'board_size': self.board.size,
            'board': [[stone.value for stone in row] for row in self.board.get_board_copy()],
            'current_player': self.current_player.color.value,
            'player1_color': self.player1.color.value,
            'player2_color': self.player2.color.value,
            'player1_name': self.player1.name,
            'player2_name': self.player2.name,
            'player1_profile': self._safe_profile(self.player1),
            'player2_profile': self._safe_profile(self.player2),
            'game_over': self.game_over,
            'winner_color': self.winner.color.value if self.winner else None,
            'history': serialized_history,
            'moves_log': self.moves_log
        }
    
    def load_state_dict(self, state: Dict[str, Any]):
        """从字典加载游戏状态"""
        self.board.set_board([[Stone(stone_value) for stone_value in row] for row in state['board']])
        
        # 恢复当前玩家
        if state['current_player'] == self.player1.color.value:
            self.current_player = self.player1
        else:
            self.current_player = self.player2
        
        self.game_over = state.get('game_over', False)
        
        # 恢复历史记录，将board值转换回Stone对象
        history_data = state.get('history', [])
        self.history = []
        for hist_state in history_data:
            restored_state = {
                'board': [[Stone(stone_value) for stone_value in row] for row in hist_state['board']],
                'current_player': hist_state['current_player'],
                'last_move': hist_state.get('last_move')
            }
            self.history.append(restored_state)

        # 恢复录像
        self.moves_log = state.get('moves_log', [])

        if 'player1_profile' in state:
            self.player1.profile = state['player1_profile']
        if 'player2_profile' in state:
            self.player2.profile = state['player2_profile']
        
        if state.get('winner_color'):
            winner_color = Stone(state['winner_color'])
            self.winner = self.player1 if self.player1.color == winner_color else self.player2
        else:
            self.winner = None
    
    @abstractmethod
    def get_game_type(self) -> str:
        """获取游戏类型"""
        pass
    
    @abstractmethod
    def _supports_pass(self) -> bool:
        """是否支持虚着"""
        pass
    
    @abstractmethod
    def _handle_pass(self) -> bool:
        """处理虚着"""
        pass
    
    @abstractmethod
    def _check_win_condition(self, position: Position) -> bool:
        """检查是否获胜"""
        pass
    
    @abstractmethod
    def _check_draw(self) -> bool:
        """检查是否平局"""
        pass

