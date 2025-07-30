from typing import Optional, Dict, Any
from ..utils.constants import (
    VISIBLE_ACTORS, INVISIBLE_ACTORS, SCENARIO_ACTORS,
    VISIBLE, INVISIBLE, SCENARIO
)

class Actor:
    """角色模型，用于管理角色属性和行为"""
    
    # 定义角色别名映射
    NAME_ALIASES = {
        'eily': 'cue',
        'eilly': 'cue',
        'm': 'M',
        'f': 'F',
        '': 'M'
    }
    
    def __init__(self, name: str, **kwargs):
        """初始化Actor对象
        
        Args:
            name: 角色名称
            **kwargs: 其他属性
        """
        if not isinstance(name, str) or not name:  # 检查非字符串或空字符串
            self.name = ""
        
        # 处理别名
        normalized_name = str(name).lower()
        if normalized_name in self.NAME_ALIASES:
            name = self.NAME_ALIASES[normalized_name]
        
        # 验证角色名称
        if name in (VISIBLE_ACTORS + INVISIBLE_ACTORS + SCENARIO_ACTORS):
            self.name = name
        else:
            self.name = "M"  # 改为默认角色而不是None
        
        for key, value in kwargs.items():
            setattr(self, key, value)
            
    @staticmethod
    def load(object: Dict) -> Optional['Actor']:
        """从字典加载Actor对象
        
        Args:
            object: 包含角色数据的字典
            
        Returns:
            Actor对象，如果加载失败则返回None
        """
        if isinstance(object, dict):
            return Actor(object.get("name"))
        return None

    def match(self, name: str) -> bool:
        """检查是否匹配指定名称
        
        Args:
            name: 要匹配的名称
            
        Returns:
            是否匹配
        """
        if not isinstance(name, str) or self.name is None:
            return False
            
        # 处理别名匹配
        normalized_name = name.lower()
        if normalized_name in self.NAME_ALIASES:
            name = self.NAME_ALIASES[normalized_name]
            
        return self.name == name

    def category(self) -> Optional[tuple]:
        """获取角色类别
        
        Returns:
            角色类别(VISIBLE_ACTORS/INVISIBLE_ACTORS/SCENARIO_ACTORS)，如果无效则返回INVISIBLE_ACTORS
        """
        if self.name:  # 检查非空字符串
            if self.name in VISIBLE_ACTORS:
                return VISIBLE_ACTORS
            elif self.name in INVISIBLE_ACTORS:
                return INVISIBLE_ACTORS
            elif self.name in SCENARIO_ACTORS:
                return SCENARIO_ACTORS
        return INVISIBLE_ACTORS  # 默认返回INVISIBLE_ACTORS

    def export(self) -> Dict[str, Any]:
        """导出为字典格式"""
        data = {"name": self.name}
        for key, value in self.__dict__.items():
            if key != "name":
                if hasattr(value, "export"):
                    data[key] = value.export()
                else:
                    data[key] = value
        return data

    def copy(self) -> 'Actor':
        """创建当前对象的深拷贝"""
        kwargs = {
            key: value.copy() if hasattr(value, "copy") else value \
            for key, value in self.__dict__.items() \
            if key != "name"
        }
        return Actor(name=self.name or "", **kwargs)  # 确保name不为None