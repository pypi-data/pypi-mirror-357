from typing import Union, Optional, List
from .mtext import MText
from ..utils.constants import DEFAULT_LANGUAGE, BULLET_KEY

class MList:
    """多语言列表类，支持单语言列表或多语言字典格式的列表
    
    Attributes:
        _data (dict): 内部存储的语言-列表字典
    """
    def __init__(self, value: Union[str, list, dict[str, list], 'MList'], language: str = None):
        """初始化MList对象
        
        Args:
            value: 列表内容，可以是字符串、列表、语言字典或MList对象
            language: 指定语言代码，仅在value为字符串或列表时使用
        """
        self._data: dict[str, list] = {}
        self._normalize_data(value, language)
    
    def _normalize_data(self, value: Union[str, list, dict, 'MList'], language: str = None) -> None:
        """规范化输入数据为内部字典格式"""
        if isinstance(value, MList):
            self._data = value._data.copy()
        elif isinstance(value, str):
            if value.strip():  # 只接受非空白字符串
                lang = language or DEFAULT_LANGUAGE
                self._data[lang] = [value]
        elif isinstance(value, list):
            if value:  # 只接受非空列表
                lang = language or DEFAULT_LANGUAGE
                self._data[lang] = [item for item in value if isinstance(item, str) and item.strip()]
        elif isinstance(value, dict):
            self._data = {
                k: [item for item in v if isinstance(item, str) and item.strip()]
                for k, v in value.items()
                if isinstance(v, list) and v
            }
    
    @property
    def default_list(self) -> Optional[list]:
        """获取默认语言的列表"""
        return self._data.get(DEFAULT_LANGUAGE) or self._data.get(next(iter(self._data), None))
    
    def get_list(self, language: str) -> list:
        """获取指定语言的列表"""
        return self._data.get(language, [])
    
    def get_text_by_pos(self, pos: int) -> Optional[MText]:
        """获取指定位置的多语言文本
        
        Args:
            pos: 列表索引位置
            
        Returns:
            MText对象，如果位置无效则返回None
        """
        if not self.default_list or pos < 0 or pos >= len(self.default_list):
            return None
            
        result = {}
        for lang, items in self._data.items():
            if pos < len(items):
                result[lang] = items[pos]
        return MText(result) if result else None
    
    def merge(self, other: Union[str, list, dict, 'MList']) -> 'MList':
        """合并其他列表数据，返回新对象"""
        result = MList(self)
        if isinstance(other, (str, list, dict, MList)):
            new_list = MList(other)
            # 保留原有的列表，只添加新的语言版本
            for lang, items in new_list._data.items():
                if lang not in result._data:
                    result._data[lang] = items
        return result

    def export(self) -> Union[list, dict, None]:
        """导出数据，根据内容返回合适的格式"""
        if not self._data:
            return None
        if len(self._data) == 1 and DEFAULT_LANGUAGE in self._data:
            return self._data[DEFAULT_LANGUAGE].copy()
        return {k: v.copy() for k, v in self._data.items()}
    
    def __eq__(self, other: Union[list, 'MList']) -> bool:
        if isinstance(other, list):
            return self.default_list == other
        if isinstance(other, MList):
            return self._data == other._data
        return False
    
    def __bool__(self) -> bool:
        """只有当存在非空列表时才返回True"""
        return bool(self._data and any(self._data.values()))
        
    def copy(self) -> 'MList':
        """创建当前对象的深拷贝"""
        return MList(self) 