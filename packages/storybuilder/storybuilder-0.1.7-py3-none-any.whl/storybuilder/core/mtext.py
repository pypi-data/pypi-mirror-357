from typing import Union, Optional

from ..utils.constants import DEFAULT_LANGUAGE

class MText:
    """多语言文本类,支持单语言字符串或多语言字典格式
    
    Attributes:
        _data (dict): 内部存储的语言-文本字典
    """
    def __init__(self, value: Union[str, dict[str, str], 'MText'], language: str = None):
        """初始化MText对象
        
        Args:
            value: 文本内容,可以是字符串、语言字典或MText对象
            language: 指定语言代码,仅在value为字符串时使用
        """
        self._data: dict[str, str] = {}
        self._normalize_data(value, language)
    
    def _normalize_data(self, value: Union[str, dict, 'MText'], language: str = None) -> None:
        """规范化输入数据为内部字典格式"""
        if isinstance(value, MText):
            self._data = value._data.copy()
        elif isinstance(value, str):
            if value.strip():  # 只接受非空白字符串
                lang = language or DEFAULT_LANGUAGE
                self._data[lang] = value
        elif isinstance(value, dict):
            self._data = {
                k: v for k, v in value.items() 
                if isinstance(v, str) and v.strip()  # 只接受非空白字符串
            }
    
    @property
    def default_text(self) -> Optional[str]:
        """获取默认语言的文本"""
        return self._data.get(DEFAULT_LANGUAGE) or self._data.get(next(iter(self._data), None))
    
    def get_text(self, language: str) -> Optional[str]:
        """获取指定语言的文本"""
        return self._data.get(language)
    
    def set_text(self, text: str, language: str = DEFAULT_LANGUAGE) -> None:
        """设置指定语言的文本"""
        if isinstance(text, str) and text.strip():
            self._data[language] = text.strip()
            
    def merge(self, other: Union[str, dict, 'MText']) -> 'MText':
        """合并其他文本数据,返回新对象"""
        result = MText(self)
        if isinstance(other, (str, dict, MText)):
            new_text = MText(other)
            # 保留原有的文本,只添加新的语言版本
            for lang, text in new_text._data.items():
                if lang not in result._data:
                    result._data[lang] = text
        return result

    def export(self) -> Union[str, dict, None]:
        """导出数据,根据内容返回合适的格式"""
        if not self._data:
            return None
        if len(self._data) == 1 and DEFAULT_LANGUAGE in self._data:
            return self._data[DEFAULT_LANGUAGE]
        return self._data.copy()
    
    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return self.default_text == other
        if isinstance(other, MText):
            return self._data == other._data
        return False
    
    def __bool__(self) -> bool:
        """只有当存在非空文本时才返回True"""
        return bool(self._data)
        
    def copy(self) -> 'MText':
        return MText(self) 