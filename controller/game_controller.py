"""
游戏控制器
"""
from typing import Optional
from ..core.game import Game
from ..core.game_factory import GameFactory
from ..core.player import Player
from ..core.human_player import HumanPlayer
from ..core.ai_player import SuperAI
from ..core.stone import Stone
from ..core.position import Position
from ..persistence.file_manager import FileManager
from ..exceptions import (
    InvalidMoveException, GameOverException, NoHistoryException,
    FileOperationException, InvalidInputException
)


class GameController:
    """游戏控制器"""
    
    def __init__(self):
        self.game: Optional[Game] = None
        self.file_manager = FileManager()
        self.ai_player: Optional[SuperAI] = None
    
    def start_game(self, game_type: str, board_size: int, 
                   mode: str, human_color: Optional[str] = None) -> str:
        """开始游戏"""
        try:
            # 创建玩家
            if mode == "human":
                # 本地双人对战
                player1 = HumanPlayer(Stone.BLACK, "黑方")
                player2 = HumanPlayer(Stone.WHITE, "白方")
            else:
                # 人机对战
                if human_color is None or human_color == "black":
                    human = HumanPlayer(Stone.BLACK, "玩家")
                    ai = SuperAI(Stone.WHITE, "超级AI")
                    player1, player2 = human, ai
                else:
                    human = HumanPlayer(Stone.WHITE, "玩家")
                    ai = SuperAI(Stone.BLACK, "超级AI")
                    player1, player2 = ai, human
                
                self.ai_player = ai
            
            # 创建游戏
            self.game = GameFactory.create_game(game_type, board_size, player1, player2)
            
            return f"游戏已开始! 游戏类型: {game_type}, 棋盘大小: {board_size}x{board_size}, 模式: {mode}"
        except Exception as e:
            return f"开始游戏失败: {str(e)}"
    
    def place_stone(self, position: Position) -> str:
        """落子"""
        if not self.game:
            return "请先开始游戏"
        
        # 检查是否是AI回合，AI回合时不允许玩家落子
        if self.is_ai_turn():
            return "AI回合不能落子，请等待AI落子"
        
        try:
            result = self.game.make_move(position)
            
            # 更新AI的对手落子信息（如果对手是人类玩家）
            # 落子后current_player已经切换，所以需要检查切换后的玩家
            if self.ai_player:
                # 如果当前玩家是AI，说明上一步是人类玩家
                if self.game.current_player == self.ai_player:
                    self.ai_player.update_opponent_move(position)
            
            if not result:
                # 游戏结束
                if self.game.winner:
                    return f"游戏结束! {self.game.winner.name} 获胜!"
                else:
                    return "游戏结束! 平局!"
            else:
                return f"落子成功: {position}"
        except InvalidMoveException as e:
            return f"无效落子: {str(e)}"
        except GameOverException as e:
            return f"游戏已结束: {str(e)}"
        except Exception as e:
            return f"落子失败: {str(e)}"
    
    def pass_move(self) -> str:
        """虚着（仅围棋）"""
        if not self.game:
            return "请先开始游戏"
        
        # 检查是否是AI回合，AI不能虚着
        if self.is_ai_turn():
            return "AI回合不能虚着"
        
        try:
            result = self.game.make_move(None)
            if not result:
                if self.game.winner:
                    return f"游戏结束! {self.game.winner.name} 获胜!"
                else:
                    return "游戏结束! 平局!"
            else:
                return "虚着成功"
        except InvalidMoveException as e:
            return f"无效操作: {str(e)}"
        except Exception as e:
            return f"虚着失败: {str(e)}"
    
    def undo_move(self) -> str:
        """悔棋（撤销自己和对手各一步）"""
        if not self.game:
            return "请先开始游戏"
        
        # 检查是否是AI回合，如果是则不允许悔棋
        if self.is_ai_turn():
            return "AI回合不能悔棋，请等待AI落子"
        
        try:
            # 检查是否可以悔棋两步
            if self.game.can_undo_two():
                # 悔棋两步：撤销对手的落子和自己的落子
                self.game.undo_two()
                return "悔棋成功（已撤销两步）"
            elif self.game.can_undo():
                # 如果只有一步历史，只悔一步
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
        
        # 检查是否是AI回合，AI不能认负
        if self.is_ai_turn():
            return "AI不能认负"
        
        try:
            self.game.resign(self.game.current_player)
            return f"{self.game.current_player.name} 投子认负! {self.game.winner.name} 获胜!"
        except Exception as e:
            return f"认负失败: {str(e)}"
    
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
            
            # 创建玩家
            player1_color = Stone(game_state['player1_color'])
            player2_color = Stone(game_state['player2_color'])
            
            player1_name = game_state.get('player1_name', '')
            player2_name = game_state.get('player2_name', '')
            
            # 判断是否是AI玩家
            if "AI" in player1_name or "超级AI" in player1_name:
                player1 = SuperAI(player1_color, player1_name)
                player2 = HumanPlayer(player2_color, player2_name)
                self.ai_player = player1
            elif "AI" in player2_name or "超级AI" in player2_name:
                player1 = HumanPlayer(player1_color, player1_name)
                player2 = SuperAI(player2_color, player2_name)
                self.ai_player = player2
            else:
                player1 = HumanPlayer(player1_color, player1_name)
                player2 = HumanPlayer(player2_color, player2_name)
                self.ai_player = None
            
            # 创建游戏
            self.game = GameFactory.create_game(
                game_state['game_type'],
                game_state['board_size'],
                player1,
                player2
            )
            
            # 加载状态
            self.game.load_state_dict(game_state)
            
            return f"游戏已从 {filename} 加载"
        except FileOperationException as e:
            return f"加载失败: {str(e)}"
        except Exception as e:
            return f"加载失败: {str(e)}"
    
    def restart_game(self) -> str:
        """重新开始游戏"""
        if not self.game:
            return "没有正在进行的游戏"
        
        game_type = self.game.get_game_type()
        board_size = self.game.board.size
        
        # 判断模式
        if self.ai_player:
            mode = "ai"
            # 判断人类玩家颜色
            human_player = self.game.player1 if self.game.player1 != self.ai_player else self.game.player2
            human_color = "black" if human_player.color == Stone.BLACK else "white"
        else:
            mode = "human"
            human_color = None
        
        # 重置AI状态
        if self.ai_player:
            self.ai_player.reset()
        
        return self.start_game(game_type, board_size, mode, human_color)
    
    def get_game(self) -> Optional[Game]:
        """获取当前游戏"""
        return self.game
    
    def is_ai_turn(self) -> bool:
        """判断是否是AI回合"""
        return self.ai_player is not None and self.game and self.game.current_player == self.ai_player
    
    def make_ai_move(self) -> str:
        """执行AI落子"""
        if not self.is_ai_turn():
            return "不是AI回合"
        
        try:
            position = self.ai_player.make_move(self.game)
            # AI落子直接调用游戏逻辑，不经过place_stone的检查
            result = self.game.make_move(position)
            
            if not result:
                # 游戏结束
                if self.game.winner:
                    return f"游戏结束! {self.game.winner.name} 获胜!"
                else:
                    return "游戏结束! 平局!"
            else:
                return f"AI落子成功: {position}"
        except InvalidMoveException as e:
            return f"AI落子失败: {str(e)}"
        except GameOverException as e:
            return f"游戏已结束: {str(e)}"
        except Exception as e:
            return f"AI落子失败: {str(e)}"

