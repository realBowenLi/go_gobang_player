"""
序列化器
"""
import json
from typing import Dict, Any
from ..exceptions import FileOperationException


class JSONSerializer:
    """JSON序列化器"""
    
    @staticmethod
    def serialize(data: Dict[str, Any], filename: str):
        """序列化数据到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            raise FileOperationException(f"保存文件失败: {str(e)}")
        except Exception as e:
            raise FileOperationException(f"序列化失败: {str(e)}")
    
    @staticmethod
    def deserialize(filename: str) -> Dict[str, Any]:
        """从文件反序列化数据"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            raise FileOperationException(f"文件不存在: {filename}")
        except json.JSONDecodeError as e:
            raise FileOperationException(f"文件格式错误: {str(e)}")
        except IOError as e:
            raise FileOperationException(f"读取文件失败: {str(e)}")
        except Exception as e:
            raise FileOperationException(f"反序列化失败: {str(e)}")

