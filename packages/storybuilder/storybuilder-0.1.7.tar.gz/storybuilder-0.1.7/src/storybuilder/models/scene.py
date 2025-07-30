from typing import Optional, Dict
import copy

class Scene:
    """场景模型，用于管理场景属性"""
    
    def __init__(self, scene: Optional[str] = None, index: Optional[str] = None, bgColor: Optional[str] = None):
        """初始化Scene对象
        
        Args:
            scene: 场景标识
            index: 场景索引
            bgColor: 背景颜色
        """
        self.scene = scene
        self.index = index
        self.bgColor = bgColor

    @staticmethod
    def load(object: Dict) -> 'Scene':
        """从字典加载Scene对象
        
        Args:
            object: 包含场景数据的字典
            
        Returns:
            Scene对象
        """
        if isinstance(object, str):
            return Scene(scene=object)
        elif isinstance(object, dict):
            if "scene" in object:
                return Scene(object.get("scene", None))
            else:
                return Scene(
                    index=object.get("index", None),
                    bgColor=object.get("bgColor", None)
                )
        return Scene()

    def copy(self) -> 'Scene':
        """创建当前对象的深拷贝"""
        return copy.deepcopy(self)
    
    def export(self) -> Dict:
        """导出为字典格式
        
        Returns:
            包含场景数据的字典
        """
        result = None
        if isinstance(self.scene, str):
            result = self.scene
        else:
            data = {}
            if isinstance(self.index, str) and len(self.index) > 0:
                data["index"] = self.index
            if isinstance(self.bgColor, str) and len(self.bgColor) > 0:
                data["bgColor"] = self.bgColor
            if len(data) > 0:
                result = data
    
        return result 