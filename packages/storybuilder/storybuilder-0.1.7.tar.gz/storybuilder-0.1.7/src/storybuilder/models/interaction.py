from typing import Optional, List, Dict, Any, Union
import copy
from .content import Content
from .script import Script
from ..utils.constants import SCENARIO_ACTOR_EXAM

class Interaction:
    """交互模型，用于管理交互行为"""
    
    def __init__(self, 
                 actor_name: Optional[str] = None,
                 start: Optional[str] = None, 
                 duration: Optional[str] = None, 
                 content: Optional[Content] = None,
                 figure: Optional[int] = None,
                 position: Optional[List[float]] = None,
                 transform: Optional[str] = None,
                 onResult: Optional[Any] = None,
                 onPoster: Optional[Any] = None,
                 type: Optional[str] = None,
                 script: Optional[Script] = None):
        """初始化Interaction对象"""
        self.start = start
        self.duration = duration
        self.onResult = onResult
        self.onPoster = onPoster
        self.actor_name = actor_name
        self.figure = figure
        self.position = position
        self.transform = transform
        self.content = content if isinstance(content, Content) else Content()
        self.type = type
        self.script = script

    @staticmethod
    def load(data: Dict) -> 'Interaction':
        """从字典加载Interaction对象"""
        return Interaction(
            actor_name=data.get("actor_name"),
            start=data.get("start"),
            duration=data.get("duration"),
            content=Content.load(data.get("content")),
            figure=data.get("figure"),
            position=data.get("position"),
            transform=data.get("transform"),
            onResult=data.get("onResult"),
            onPoster=data.get("onPoster"),
            type=data.get("type"),
            script=Script.load(data.get("script"))
        )

    def copy(self) -> 'Interaction':
        """创建当前对象的深拷贝"""
        return copy.deepcopy(self)
    
    def merge(self, interaction: 'Interaction') -> 'Interaction':
        """合并另一个交互对象
        
        Args:
            interaction: 要合并的交互对象
            
        Returns:
            合并后的新交互对象
        """
        updated = self.copy()
        if isinstance(interaction, Interaction):
            updated.start = interaction.start if interaction.start != None else updated.start
            updated.duration = interaction.duration if interaction.duration != None else updated.duration
            updated.onResult = interaction.onResult if interaction.onResult != None else updated.onResult
            updated.onPoster = interaction.onPoster if interaction.onPoster != None else updated.onPoster
            updated.actor_name = interaction.actor_name if interaction.actor_name != None else updated.actor_name
            updated.figure = interaction.figure if interaction.figure != None else updated.figure
            updated.position = interaction.position if interaction.position != None else updated.position
            updated.transform = interaction.transform if interaction.transform != None else updated.transform
            updated.content = interaction.content if interaction.content.export() != None else updated.content
            updated.type = interaction.type if interaction.type != None else updated.type
            updated.script = interaction.script if interaction.script != None else updated.script
        return updated
    
    def export(self, id: Optional[int] = None) -> Optional[Dict]:
        """导出为字典格式
        
        Returns:
            包含交互数据的字典，如果数据不完整则返回None
        """
        data = {}
        
        data["start"] = self.start if self.start else ""
        data["duration"] = self.duration if self.duration else "auto"
        if isinstance(self.content, Content) and self.content.export() != None:
            data["content"] = self.content.export()
        if id is not None:
            data["actor"] = id if id > -1 else -1
        else:
            if self.actor_name is not None:
                data["actor_name"] = self.actor_name
        if self.figure is not None:
            data["figure"] = self.figure
        if self.position is not None and isinstance(self.position, list):
            data["position"] = self.position
        if self.transform is not None and isinstance(self.transform, str) and len(self.transform) > 0:
            data["transform"] = self.transform
        if self.type is not None:
            data["type"] = self.type
        if self.onResult is not None:
            data["onResult"] = self.onResult
        if self.onPoster is not None:
            data["onPoster"] = self.onPoster
        if self.script is not None and self.script.export():
            data["script"] = self.script.export()

        # 只要有type就认为是有效的交互。
        return data if len(data.keys()) > 2 else None
    
    def export_scripts(self) -> Optional[Dict]:
        data = {}
        if self.script is not None:
            data["script"] = self.script.export()
        return data

class PostureInteraction(Interaction):
    """姿势交互模型，用于管理角色姿势相关的交互"""
    
    def __init__(self, 
                 actor_name: Optional[str] = None,
                 figure: Optional[int] = None,
                 position: Optional[List[float]] = None,
                 transform: Optional[str] = None,
                 start: Optional[str] = None,
                 duration: Optional[str] = None,
                 onResult: Optional[Any] = None,
                 onPoster: Optional[Any] = None):
        """初始化PostureInteraction对象"""
        super().__init__(
            type="motion",
            actor_name=actor_name,
            figure=figure,
            position=position,
            transform=transform,
            start=start,
            duration=duration,
            onResult=onResult,
            onPoster=onPoster
        )

class ExamInitInteraction(Interaction):
    """初始化交互类"""
    ON_RESULT: int = 0
    POPUP: int = 4
    
    def __init__(self, actor_name: Optional[str] = None,
                    text: Optional[Union[str, Dict[str, str]]] = None,
                    voice: Optional[int] = None, 
                    script: Optional[Script] = None) -> None:
        super().__init__(
            onResult=self.ON_RESULT,
            actor_name=actor_name if actor_name else SCENARIO_ACTOR_EXAM,
            type="talk",
            content=Content(popup=self.POPUP, voice=voice, text=text),
            script=script
        )

class ExamErrorInteraction(Interaction):
    """错误交互类"""
    ON_RESULT: int = -1
    POPUP: int = 4
    
    def __init__(self, actor_name: Optional[str] = None,
                    text: Optional[Union[str, Dict[str, str]]] = None,
                    voice: Optional[int] = None,
                    script: Optional[Script] = None) -> None:
        super().__init__(
            onResult=self.ON_RESULT,
            actor_name=actor_name if actor_name else SCENARIO_ACTOR_EXAM,
            type="talk",
            content=Content(popup=self.POPUP, voice=voice, text=text),
            script=script
        )

class ExamSuccessInteraction(Interaction):
    """成功交互类"""
    POPUP: int = 2
    
    def __init__(self, actor_name: Optional[str] = None,
                    onResult: Optional[int] = None,
                    text: Optional[Union[str, Dict[str, str]]] = None,
                    voice: Optional[int] = None,
                    script: Optional[Script] = None) -> None:
        super().__init__(
            onResult=onResult,
            actor_name=actor_name if actor_name else SCENARIO_ACTOR_EXAM,
            type="talk",
            content=Content(popup=self.POPUP, voice=voice, text=text),
            script=script
        )
        
