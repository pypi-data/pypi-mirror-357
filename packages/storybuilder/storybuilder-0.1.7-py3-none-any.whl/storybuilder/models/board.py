from typing import Optional, List, Dict, Any, Tuple, Union
from .content import Content
from .script import Script, MText
from ..utils.constants import warn_print, error_print, info_print, debug_print
import uuid
import re

class Board:
    """画板模型，用于管理内容展示"""
    
    def __init__(self, type: str = None, content: Content = None, 
                 rect: list = None, contentList: list = None):
        """初始化Board对象
        
        Args:
            type: 画板类型
            content: 主要内容
            rect: 矩形区域
            contentList: 内容列表
        """
        self._type = type  # board层级的type
        self._rect = rect[:4] if (isinstance(rect, list) and len(rect)>=4) else None  # board层级的rect
        self.content = content if isinstance(content, Content) else Content()
        self.contentList = contentList if isinstance(contentList, list) else []

    @staticmethod
    def load(object: dict) -> Optional['Board']:
        """从字典加载Board对象"""
        if not isinstance(object, dict):
            return None
        
        # 获取board层级的rect和type
        board_rect = object.get("rect")[:4] if isinstance(object.get("rect"), list) and len(object["rect"]) >= 4 else None
        board_type = object.get("type")
        
        # 加载content
        loaded_content = None
        loaded_content_list = []
        if object.get("content"):
            if isinstance(object.get("content"), dict):
                debug_print(f"Board.load - content is a dict")
                loaded_content = Content.load(object.get("content")) if object.get("content") else None
            elif isinstance(object.get("content"), list):
                debug_print(f"Board.load - content is a list")
                for i, content_obj in enumerate(object.get("content")):
                    if content_obj := Content.load(content_obj):
                        if i == 0 and loaded_content is None:
                            loaded_content = content_obj
                        else:
                            loaded_content_list.append(content_obj)
        
        # 加载内容列表
        if isinstance(object.get("contentList"), list):
            object_content_list = object.get("contentList")
            for content_entry in object_content_list:
                if content_entry_obj := Content.load(content_entry):
                    loaded_content_list.append(content_entry_obj)
                    
        # 创建Board对象
        board = Board(
            type=board_type,
            rect=board_rect,
            content=loaded_content
        )

        if len(loaded_content_list) > 0:
            board.contentList=loaded_content_list

        return board

    def copy(self) -> 'Board':
        """创建当前对象的深拷贝"""
        return Board(
            content=self.content.copy() if self.content else None,
            type=self._type,
            rect=self._rect[:] if self._rect else None,
            contentList=[content.copy() for content in self.contentList] if self.contentList else None
        )

    def export(self) -> Optional[dict]:
        """导出为字典格式
        
        Returns:
            包含画板数据的字典，如果没有数据则返回None
        """
        data = {}

        # 导出board层级的type
        if self._type is not None:
            data["type"] = self._type

        # 导出board层级的rect
        if self._rect is not None:
            data["rect"] = self._rect
            
        # 导出内容
        if isinstance(self.content, Content):
            if content_data := self.content.export():
                data["content"] = content_data                
            
        # 导出内容列表
        if self.contentList:
            data["contentList"] = []
            for content in self.contentList:
                if isinstance(content, Content) and (content_data := content.export()):
                    if (content_data.get("image") or content_data.get("src")) and content_data.get("caption", None) is None:
                        content_data["caption"] = ""
                    data["contentList"].append(content_data)
                else:
                    warn_print(f"Invalid Content instance {content}")

        return data if data else {}

    @property
    def type(self) -> Optional[str]:
        """获取type属性，优先返回board层级的type，如果不存在则返回content的type"""
        return self._type if self._type is not None else (
            self.content.type if isinstance(self.content, Content) else None
        )

    @type.setter
    def type(self, value: str):
        self._type = value

    @property
    def rect(self) -> Optional[list]:
        """获取rect属性，优先返回board层级的rect，如果不存在则返回content的rect"""
        return self._rect if self._rect is not None else (
            self.content.rect if isinstance(self.content, Content) else None
        )

    @rect.setter
    def rect(self, value: list):
        self._rect = value
