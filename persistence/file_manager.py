"""
文件管理器
"""
import os
from typing import Dict, Any
from .serializer import JSONSerializer
from ..exceptions import FileOperationException


class FileManager:
    """文件管理器"""
    
    def __init__(self):
        self.serializer = JSONSerializer()
    
    def save_game(self, game_state: Dict[str, Any], filename: str):
        """保存游戏状态"""
        # 验证文件名
        if not filename:
            raise FileOperationException("文件名不能为空")
        
        # 确保目录存在
        directory = os.path.dirname(filename) if os.path.dirname(filename) else '.'
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as e:
                raise FileOperationException(f"创建目录失败: {str(e)}")
        
        # 序列化并保存
        self.serializer.serialize(game_state, filename)
    
    def load_game(self, filename: str) -> Dict[str, Any]:
        """加载游戏状态"""
        if not filename:
            raise FileOperationException("文件名不能为空")
        
        if not os.path.exists(filename):
            raise FileOperationException(f"文件不存在: {filename}")
        
        data = self.serializer.deserialize(filename)
        
        # 验证数据格式
        required_fields = ['game_type', 'board_size', 'board']
        for field in required_fields:
            if field not in data:
                raise FileOperationException(f"存档文件格式错误: 缺少字段 {field}")
        
        return data

