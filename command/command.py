"""
命令抽象基类
"""
from abc import ABC, abstractmethod


class Command(ABC):
    """命令抽象基类"""
    
    @abstractmethod
    def execute(self) -> str:
        """执行命令"""
        pass
    
    @abstractmethod
    def can_undo(self) -> bool:
        """是否可以撤销"""
        pass
    
    @abstractmethod
    def undo(self):
        """撤销命令"""
        pass

