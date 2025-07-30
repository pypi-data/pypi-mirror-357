from typing import Optional, Dict, List, Union, TypeVar, cast, Type, TYPE_CHECKING
from ...core import MHTML, MText, MList
from ...models import Script, ActorManager, Content, Board, Scene, Interaction, PostureInteraction, Actor, ExamSuccessInteraction, ExamErrorInteraction, ExamInitInteraction
from ...utils.constants import (
    RED, YELLOW, BLUE, RESET, DEFAULT_LANGUAGE, LOCAL_DEFAULT_ROOT,
    VISIBLE_ACTORS, INVISIBLE_ACTORS, MULTIPLE_POSTURE_ACTORS, 
    SCENARIO_ACTORS, ENDING_SOUND, SCENE_EXAM, SCENE_NOTES,
    DEBUG_MODE, SCENARIO_ACTOR_ENDING, SCENARIO_ACTOR_NOTES, 
    SCENARIO_ACTOR_EXAM, SCENARIO_ACTOR_CONCENTRAK,
    debug_print, info_print, warn_print, error_print
)
from ...config.figures import CHARACTER_FIGURE_ACCESSORY_KEYS, CHARACTER_FIGURES
from ...config.profiles import PRONUNCIATION_DICTIONARY
from ...utils.helpers import (
    normalize_math_chars, remove_emojis, fit_rect,
    get_actors, is_valid_http_url, get_image_size,
    fit_rect, has_chinese_char
)
from ...services.voice import VoiceSynthesizer
from ...services.cos import CosUploader
from ..posture_selector import PostureSelector
from .mixins import NarrationMixin, ImageMixin, QuestionMixin
import copy
import json
import os
import uuid
import random

if TYPE_CHECKING:
    from ..story import Story
# 类型变量定义
T = TypeVar('T')
PageType = TypeVar('PageType', bound='Page')

# 在 scenario.py 中添加
from enum import Enum, auto

class PageInitMode(Enum):
    """页面初始化模式"""
    NEW = auto()        # 创建新页面
    LOAD = auto()       # 从数据加载页面

class Page(QuestionMixin, NarrationMixin, ImageMixin):
    """统一的页面基类"""
    
    def __init__(self, story_instance: 'Story'):
        """初始化Page对象
        
        Args:
            page_type: 页面类型
            story_instance: Story实例
            init_mode: 初始化模式
            **kwargs: 额外参数
        """

        self.story = story_instance

        # 初始化Mixin
        self.initialize_question()
        self.initialize_narration(self.story.narrator)
        self.initialize_image()

        # 基础属性
        self.locale = self.story.locale if self.story else None

        self.page_type = None

        self._duration = None
        self._transition = None
        self.scene = None
        self.board = None
        self.actor = None

        # 交互相关
        self.mute_scripts = []
        self.interactions = []
        self.default_interactions = []
        self.note_interaction = None
        
        # Concentrak 标题
        self.title = None        
        # 结尾效果相关
        self.ending_effect = False

        debug_print(f"Page.__init__")
        
    @property
    def transition(self) -> Optional[str]:
        """获取页面过渡效果
        
        Returns:
            页面过渡效果，如果未设置则返回 None
        """
        return self._transition
        
    @transition.setter
    def transition(self, value: Optional[str]):
        """设置页面过渡效果
        
        Args:
            value: 页面过渡效果
        """
        self._transition = value
        
    @property
    def duration(self) -> Optional[str]:
        """获取页面持续时间
        
        Returns:
            页面持续时间，如果未设置则返回 None
        """
        return self._duration
        
    @duration.setter
    def duration(self, value: Optional[str]):
        """设置页面持续时间
        
        Args:
            value: 页面持续时间
        """
        self._duration = value
        
    @property
    def start(self) -> Optional[str]:
        """获取页面开始时间
        
        Returns:
            页面开始时间，如果未设置则返回 None
        """
        return getattr(self, '_start', None)
        
    @start.setter
    def start(self, value: Optional[str]):
        """设置页面开始时间
        
        Args:
            value: 页面开始时间
        """
        self._start = value

    def _manage_interactions(self, new_interaction, update_type="add"):
        """集中管理页面交互，确保只有一个可见角色的一个姿势
        
        此方法主要用于动态场景，如：
        1. 添加/更新对话时需要调整角色姿势
        2. 动更新角色状态时需要协调多个交互
        3. 处理多个交互列表（default_interactions 和 interactions）之间的姿势冲突
        
        注意：对于 set_actor 这样的静态设置，建议使用直接替换策略而不是此方法，
        因静态设置不需要处理复杂的交互状态协调。
        
        Args:
            new_interaction: 要添加或更新的新交互
            update_type: 操作类型，以 "add"（添加）, "update"（更新）, "remove"（删除）
        """
        try:
            if not new_interaction:
                return

            # 获取当前所有显示姿势的交互
            posture_interactions = [
                (i, interaction) for i, interaction in enumerate(self.default_interactions + self.interactions)
                if interaction.actor_name == new_interaction.actor_name and 
                   interaction.figure is not None and interaction.figure >= 0
            ]

            if update_type == "add":
                # 如果新交互要显示姿势（figure >= 0）
                if new_interaction.figure is not None and new_interaction.figure >= 0:
                    # 将其他所有同角色交互的 figure 设为 -1
                    for i, interaction in posture_interactions:
                        if i < len(self.default_interactions):
                            self.default_interactions[i].figure = -1
                        else:
                            self.interactions[i - len(self.default_interactions)].figure = -1
                # 如果已经有显示姿势的交互，新交互的 figure 应该为 -1
                elif posture_interactions:
                    new_interaction.figure = -1

            elif update_type == "update":
                # 如果更新后要显示姿势，需要处理其他交互
                if new_interaction.figure is not None and new_interaction.figure >= 0:
                    for i, interaction in posture_interactions:
                        if i < len(self.default_interactions):
                            if self.default_interactions[i] != new_interaction:
                                self.default_interactions[i].figure = -1
                        else:
                            if self.interactions[i - len(self.default_interactions)] != new_interaction:
                                self.interactions[i - len(self.default_interactions)].figure = -1

            elif update_type == "remove":
                # 如果删除的是显示姿势的交互，可以选择其他交互显示姿势
                if posture_interactions and posture_interactions[0][1] == new_interaction:
                    # 可以选择另一个交互来显示姿势
                    remaining_interactions = [
                        (i, interaction) for i, interaction in enumerate(self.default_interactions + self.interactions)
                        if interaction.actor_name == new_interaction.actor_name and interaction != new_interaction
                    ]
                    if remaining_interactions:
                        i, interaction = remaining_interactions[0]
                        if i < len(self.default_interactions):
                            self.default_interactions[i].figure = new_interaction.figure
                        else:
                            self.interactions[i - len(self.default_interactions)].figure = new_interaction.figure

        except Exception as e:
            self._handle_error(e, "_manage_interactions")

    def _handle_error(self, error: Exception, method_name: str):
        """处理错误
        
        Args:
            error: 异常对象
            method_name: 方法名称
            
        Raises:
            Exception: 重新抛出带有上下文的异常
        """
        error_msg = f"Error in {self.__class__.__name__} ({method_name}): {str(error)}"
        error_print(error_msg)  # 记录错误
        raise Exception(error_msg)  # 重新抛出异常

    def apply_style(self, style_object: Dict):
        """应用样式

        Args:
            style_object: 样式对象
        """
        for i, page in enumerate(self.story._pages):
            if page == self:
                page_id = float(i)
                break
        if "scenarios" in style_object:
            if self.page_type in style_object["scenarios"]:
                scene_value = style_object["scenarios"][self.page_type]
                if isinstance(scene_value, str):
                    self.scene = Scene(scene=scene_value)
                    debug_print("Page.apply_style", "- scene:", self.scene.export(),
                                "page_type:", self.page_type, f"")
                elif isinstance(scene_value, dict) and "scene" in scene_value:
                    self.scene = Scene(scene=scene_value["scene"])
                    debug_print("Page.apply_style", "- scene scene:", self.scene.export(),
                                "page_type:", self.page_type, f"")
                elif isinstance(scene_value, dict):
                    self.scene = Scene(
                        index = scene_value.get("index", None),
                        bgColor = scene_value.get("bgColor", None)
                    )
                    debug_print("Page.apply_style", "- scene dict:", self.scene.export(),
                                "page_type:", self.page_type, f"")

        if "frame" in style_object and self.board and self.board.content:
            self.board.content.border = style_object["frame"] if self.board and self.board.content and self.board.content.border else None
            for i, content in enumerate(self.board.contentList):
                self.board.contentList[i].border = style_object["frame"] if content and content.border else None

        if "positions" in style_object:
            old_positions = self.story.styles["positions"] if self.story.styles and self.story.styles["positions"] else None
            new_positions = style_object["positions"]
            self.update_actor_position(old_positions, new_positions)

        if "popup" in style_object:
            new_dialog_popup = style_object["popup"]
            self.update_dialog_popup(None, new_dialog_popup)

        if "transform" in style_object and style_object["transform"] is not None:
            new_transform = style_object["transform"]
            self.update_actor_transform(None, new_transform)

    def update_actor_position(self, old_positions: Dict, new_positions: Dict):
        """更新角色位置"""
        posture_interactions = [
                        (i, interaction) for i, interaction in enumerate(self.default_interactions + self.interactions)
                    ]            
        for i, interaction_tuple in enumerate(posture_interactions):
            interaction = interaction_tuple[1]
            if (isinstance(interaction, Interaction) or isinstance(interaction, PostureInteraction)) \
                and hasattr(interaction, 'actor_name') and interaction.actor_name in VISIBLE_ACTORS \
                and hasattr(interaction, 'figure') and interaction.figure and interaction.figure > -1:
                current_actor_name = interaction.actor_name
                current_figure_id = interaction.figure
                current_figure_name = CHARACTER_FIGURES[current_actor_name][current_figure_id]

                if "boy" in current_figure_name or "sports-boy" in current_figure_name:
                    if "half" in current_figure_name:
                        if i < len(self.default_interactions):
                            self.default_interactions[i].position = new_positions["right-bottom"]
                        else:
                            self.interactions[i - len(self.default_interactions)].position = new_positions["right-bottom"]
                    elif "standright" in current_figure_name:
                        if i < len(self.default_interactions):
                            self.default_interactions[i].position = new_positions["right"]
                        else:
                            self.interactions[i - len(self.default_interactions)].position = new_positions["right"]
                    elif "-stand-" in current_figure_name:
                        if i < len(self.default_interactions):
                            self.default_interactions[i].position = new_positions["left"]
                        else:
                            self.interactions[i - len(self.default_interactions)].position = new_positions["left"]
                elif "girl" in current_figure_name:
                    if "half" in current_figure_name:
                        if i < len(self.default_interactions):
                            self.default_interactions[i].position = new_positions["right-bottom"]
                    elif "-stand-" in current_figure_name:
                        if i < len(self.default_interactions):
                            self.default_interactions[i].position = new_positions["right"]
                        else:
                            self.interactions[i - len(self.default_interactions)].position = new_positions["right"]

    def update_actor_transform(self, old_transform: str, new_transform: str):
        """更新角色变换"""
        posture_interactions = [
                        (i, interaction) for i, interaction in enumerate(self.default_interactions + self.interactions)
                    ]
        for i, interaction_tuple in enumerate(posture_interactions):
            interaction = interaction_tuple[1]
            if (isinstance(interaction, Interaction) or isinstance(interaction, PostureInteraction)) \
                and interaction.actor_name in VISIBLE_ACTORS \
                and hasattr(interaction, 'figure') and interaction.figure and interaction.figure > -1:
                if i < len(self.default_interactions):
                    self.default_interactions[i].transform = new_transform
                else:
                    self.interactions[i - len(self.default_interactions)].transform = new_transform

    def update_dialog_popup(self, old_dialog_popup: int, new_dialog_popup: int):
        """更新对话出样式"""
        posture_interactions = [
                        (i, interaction) for i, interaction in enumerate(self.default_interactions + self.interactions)
                    ]
        for i, interaction_tuple in enumerate(posture_interactions):
            interaction = interaction_tuple[1]
            if hasattr(interaction, 'content') and interaction.content \
                and hasattr(interaction.content, 'popup') and interaction.content.popup \
                and interaction.content.popup not in (2, 4, 6):
                if i < len(self.default_interactions):
                    self.default_interactions[i].content.popup = new_dialog_popup
                else:
                    self.interactions[i - len(self.default_interactions)].content.popup = new_dialog_popup

    def _filter_figure(self, figure: str, exclude_accessories: bool = True) -> bool:
        """判断姿势是否应该被过滤掉
        
        Args:
            figure: 姿势名称
            exclude_accessories: 是否排除配件姿势
            
        Returns:
            bool: True表示保留该姿势，False表示过滤掉
        """
        if not exclude_accessories:
            return True
            
        return not any(accessory in figure for accessory in CHARACTER_FIGURE_ACCESSORY_KEYS)

    def _get_available_figures(self, current_actor_figures: List[str], exclude_accessories: bool = True) -> List[Dict]:
        """获取可用的姿势列表
        
        Args:
            current_actor_figures: 当前角色的所有姿势
            exclude_accessories: 是否排除配件姿势
            
        Returns:
            List[Dict]: 可用姿势列表，每个元素包含index和figure
        """
        return [
            {"index": j, "figure": figure}
            for j, figure in enumerate(current_actor_figures)
            if self._filter_figure(figure, exclude_accessories)
        ]

    def set_actor(self, actor: str, postures=None, key_scenario="-stand-", exclude_accessories=True):
        """设置角色及其姿势和位置
        
        此方法使用直接替换策略而不是交互管理器（_manage_interactions），原因是：
        1. 设置角色是一个静态操作，不需要处理复杂的交互状态协调
        2. 通过直接清除所有旧的姿势交互添加新的交互，以确保状态的一致性
        3. 姿势交互只存在于 default_interactions 中，不会影响 interactions 中的其他交互
        
        Args:
            actor_name: 角色名称
            postures: 姿势名称或姿势列表，如果为None则使用默认姿势
            key_scenario: 关键，默认为"stand"
            exclude_accessories: 是否排除配件，默认为True
        """
        if not self.features.get('enable_actor', False):
            return
        
        debug_print(f"Page.set_actor - actor:", actor)
        try:
            # 设置角色
            self.actor = actor
            
            new_key_scenario = key_scenario \
                if self.page_type not in (SCENE_EXAM, SCENE_NOTES) else "half"
            new_transform = self.story.styles.get("transform", None) \
                if self.page_type not in (SCENE_EXAM, SCENE_NOTES) else \
                    self.story.styles['scenarios'][self.page_type].get("transform", None)

            # 获取姿势ID和位置
            figure_id = self.story._posture_selector.select_posture(
                actor_name=self.actor, 
                postures=postures if postures is not None else [], 
                key_scenario=new_key_scenario, 
                exclude_accessories=exclude_accessories)
            position = self.story._get_posture_position(
                actor_name=self.actor, 
                figure_id=figure_id, 
                key_scenario=new_key_scenario
            )
            
            # 创建新的姿势交互
            new_interaction = PostureInteraction(
                actor_name=self.actor,
                figure=figure_id,
                position=position,
                transform=new_transform
            )
            
            # 清除有的姿势交互
            self.default_interactions = [interaction for interaction in self.default_interactions 
                                      if not isinstance(interaction, PostureInteraction)]

            # 添加新的姿势交互
            self.default_interactions.append(new_interaction)
        except Exception as e:
            self._handle_error(e, "set_actor")

    def set_html(self, html, rect=None):
        """设置HTML内容"""
        self.board.content.html = MHTML(html)
        self.board.rect = rect

        exported_scripts = self.board.content.export_scripts()
        if isinstance(exported_scripts, list) and len(exported_scripts) > 0:
            self.note_interaction = Interaction(
                    actor_name=SCENARIO_ACTOR_NOTES,
                    content=Content(),
                    script=Script(
                        sound = f"voice-{uuid.uuid4()}.mp3",
                        transcript = exported_scripts[0]["transcript"],
                        alternative = exported_scripts[0]["alternative"] if "alternative" in exported_scripts[0] else None,
                        narrator = self.actor
                    )
                )

            for script in exported_scripts[1:]:
                self.mute_scripts.append(
                    Script(
                        transcript=script["transcript"]
                    )
                )
        
    def add_html(self, html, rect=None):
        """添加HTML内容"""
        if not self.features['enable_html']:
            return
            
        if isinstance(html, (str, dict)):
            if self.board.contentList is None:
                self.board.contentList = []
            if isinstance(self.board.contentList, list):
                content = Content(rect=rect)
                content.html = html  # 这会触发HTML解析
                self.board.contentList.append(content)
                
                # 同步更新脚本
                if not hasattr(self, 'board_content_list_scripts'):
                    self.board_content_list_scripts = []
                self.board_content_list_scripts.append(Script(
                    sound = f"voice-{uuid.uuid4()}.mp3",
                    transcript = MText(html),
                    narrator = self.narrator
                ))
                
    def update_html(self, pos, html, rect=None):
        """更新HTML内容"""
        if not self.features['enable_html']:
            return False
            
        if isinstance(self.board.contentList, list) and pos < len(self.board.contentList) and pos >= 0:
            content = self.board.contentList[pos]
            if content.html is not None:
                content.html = html  # 这会触发HTML解析
                if rect is not None:
                    content.rect = rect
                # 同步更新脚本
                if hasattr(self, 'board_content_list_scripts') and len(self.board_content_list_scripts) > pos:
                    self.board_content_list_scripts[pos].transcript = MText(html)
                return True
        return False
        
    def remove_html(self, pos):
        """移除HTML内容"""
        if not self.features['enable_html']:
            return False
            
        if isinstance(self.board.contentList, list) and pos < len(self.board.contentList) and pos >= 0:
            content = self.board.contentList[pos]
            if content.html is not None:
                self.board.contentList.pop(pos)
                # 同步移除脚本
                if hasattr(self, 'board_content_list_scripts') and len(self.board_content_list_scripts) > pos:
                    self.board_content_list_scripts.pop(pos)
                return True
        return False

    def set_dialog(self, text: Union[str, dict], alternative_text: Optional[str] = None, 
                   popup: Optional[int] = None, figure: Optional[int] = None,
                   position: Optional[List[float]] = None, transform: Optional[str] = None, 
                   postures: Optional[List[str]] = None, key_scenario: Optional[str] = None,
                   emotion: Optional[str] = None):
        """设置对话
        
        Args:
            text: 对话文本
            popup: 对话框样式
            figure: 姿势ID
            position: 位置
            transform: 变换
            postures: 姿势列表
            key_scenario: 关键姿势
            emotion: 情感描述（用于姿势选择）
        """
        if not self.features.get('enable_dialog', False):
            return
            
        try:
            # 创建脚本
            script = Script(
                sound=f"voice-{uuid.uuid4()}.mp3",
                transcript=MText(text),
                alternative=MText(alternative_text) if alternative_text is not None else None,
                narrator=self.actor if self.actor in VISIBLE_ACTORS + INVISIBLE_ACTORS else self.narrator
            )
            
            # 创建内容
            content = Content(
                text=MText(text),
                popup=popup if popup is not None else self.story.styles.get("popup", 4),  # 使用story中的popup样式，如果未指定则使用默认值4
                voice=-1
            )
            
            # 创建交互
            interaction = Interaction(
                type="talk",
                actor_name=self.actor,
                content=content,
                script=script
            )
            
            if len(self.interactions) > 0:
                self.interactions[0] = interaction
            else:
                # 管理交互
                self._manage_interactions(interaction)
                self.interactions = [interaction]

            # 设置姿势
            new_figure = figure
            update_figure = (emotion is not None) \
                or (isinstance(postures, list) and len(postures) > 0) \
                or (isinstance(new_figure, int) and (-1 < new_figure < len(CHARACTER_FIGURES[self.actor])))
            if update_figure and not (isinstance(new_figure, int) and (-1 < new_figure < len(CHARACTER_FIGURES[self.actor]))):
                if isinstance(postures, list) and len(postures) > 0:
                    new_figure = self.story._posture_selector.select_posture(
                        actor_name = self.actor,
                        postures = postures,
                        key_scenario = key_scenario if key_scenario is not None else "-stand-"
                    )
                else:
                    new_figure = self.story._posture_selector.get_posture(
                        actor_name=self.actor, 
                        text=MText(text).default_text, 
                        emotion=emotion,
                        key_scenario=key_scenario if key_scenario is not None else "-stand-"
                    )
            debug_print(f"Page.set_dialog - new_figure: {new_figure}")

            default_posture_interaction_found = False
            for i, interaction in enumerate(self.default_interactions):
                if isinstance(interaction, PostureInteraction):
                    if new_figure is not None:
                        self.default_interactions[i].figure=new_figure
                    if position is not None:
                        self.default_interactions[i].position=position
                    if transform is not None:
                        self.default_interactions[i].transform=transform
                    default_posture_interaction_found = True
                    break
            
            if not default_posture_interaction_found and new_figure is not None:
                self.interactions[0].figure=new_figure
                self.interactions[0].position=position \
                    or self.story._get_posture_position(
                        actor_name=self.actor, 
                        figure_id=new_figure, 
                        key_scenario=key_scenario if key_scenario is not None else "-stand-"
                    )
                self.interactions[0].transform=transform \
                    or self.story.styles['scenarios'][self.page_type].get("transform", None) \
                    or self.story.styles.get("transform", None)
            
        except Exception as e:
            self._handle_error(e, "set_dialog")
            
    def add_dialog(self, text: Union[str, dict], alternative_text: Optional[str] = None,
                   popup: Optional[int] = None, figure: Optional[int] = None,
                   position: Optional[List[float]] = None, transform: Optional[str] = None,
                   postures: Optional[List[str]] = None, key_scenario: Optional[str] = "-stand-",
                   emotion: Optional[str] = None):
        """添加对话
        
        Args:
            text: 对话文本
            popup: 对话框样式
            figure: 姿势ID
            position: 位置，如果未指定则使用默认位置
            transform: 变换
            postures: 姿势列表
            key_scenario: 关键姿势
            emotion: 情感描述（用于姿势选择）
        """

        self.add_dialog_at(
            len(self.interactions), 
            text, alternative_text, 
            popup, figure, position, 
            transform, postures, 
            key_scenario, emotion
        )
        
    def add_dialog_at(self, pos: int, text: Union[str, dict], alternative_text: Optional[str] = None,
                   popup: Optional[int] = None, figure: Optional[int] = None,
                   position: Optional[List[float]] = None, transform: Optional[str] = None,
                   postures: Optional[List[str]] = None, key_scenario: Optional[str] = "-stand-",
                   emotion: Optional[str] = None):
        """在指定位置添加对话
        
        Args:
            pos: 对话位置
            text: 对话文本
            popup: 对话框样式
            figure: 姿势ID
            position: 位置，如果未指定则使用默认位置
            transform: 变换
            postures: 姿势列表
            key_scenario: 关键姿势
            emotion: 情感描述（用于姿势选择）
        """
        if not self.features.get('enable_dialog', False):
            return
        
        if pos < 0 or pos > len(self.interactions):
            warn_print(f"Page.add_dialog_at - pos: {pos} is out of interactionsrange")
            return
            
        try:
            # 创建脚本
            script = Script(
                sound=f"voice-{uuid.uuid4()}.mp3",
                transcript=MText(text),
                alternative=MText(alternative_text) if alternative_text is not None else None,
                narrator=self.actor if self.actor in VISIBLE_ACTORS + INVISIBLE_ACTORS else self.narrator
            )
            
            # 创建内容
            content = Content(
                text=MText(text),
                popup=popup if popup is not None else self.story.styles.get("popup", 4),  # 使用story中的popup样式，如果未指定则使用默认值4
                voice=-1
            )

            # 创建交互
            interaction = Interaction(
                type="talk",
                actor_name=self.actor,
                content=content,
                script=script
            )
            
            # 管理交互
            self._manage_interactions(interaction)
            self.interactions.insert(pos, interaction)

            update_figure = (emotion is not None) \
                or (isinstance(postures, list) and len(postures) > 0) \
                or (isinstance(figure, int) and (-1 < figure < len(CHARACTER_FIGURES[self.actor])))
            if len(self.interactions) == 1 and update_figure:
                # 设置姿势
                new_figure = figure
                if not (isinstance(new_figure, int) and (-1 < new_figure < len(CHARACTER_FIGURES[self.actor]))):
                    if isinstance(postures, list) and len(postures) > 0:
                        new_figure = self.story._posture_selector.select_posture(
                            actor_name = self.actor,
                            postures = postures,
                            key_scenario = key_scenario if key_scenario is not None else "-stand-"
                        )
                    else:
                        new_figure = self.story._posture_selector.get_posture(
                            actor_name=self.actor, 
                            text=MText(text).default_text, 
                            emotion=emotion,
                            key_scenario=key_scenario if key_scenario is not None else "-stand-"
                        )
                debug_print(f"Page.add_dialog_at - new_figure: {new_figure}")

                default_posture_interaction_found = False
                for i, interaction in enumerate(self.default_interactions):
                    if isinstance(interaction, PostureInteraction):
                        self.default_interactions[i].figure=new_figure
                        if position is not None:
                            self.default_interactions[i].position=position
                        if transform is not None:
                            self.default_interactions[i].transform=transform
                        default_posture_interaction_found = True
                        break
                
                if not default_posture_interaction_found:
                    self.interactions[0].figure=new_figure
                    self.interactions[0].position=position \
                        or self.story._get_posture_position(
                            actor_name=self.actor, 
                            figure_id=new_figure, 
                            key_scenario=key_scenario if key_scenario is not None else "-stand-"
                        )
                    self.interactions[0].transform=transform \
                        or self.story.styles['scenarios'][self.page_type].get("transform", None) \
                        or self.story.styles.get("transform", None)

        except Exception as e:
            self._handle_error(e, "add_dialog_at")        
            
    def update_dialog(self, pos: int, text: Optional[Union[str, dict]] = None, alternative_text: Optional[str] = None,
                     popup: Optional[int] = None, figure: Optional[int] = None, position: Optional[List[float]] = None,
                     transform: Optional[str] = None, postures: Optional[List[str]] = None, 
                     key_scenario: Optional[str] = "-stand-", emotion: Optional[str] = None):
        """更新对话
        
        Args:
            pos: 对话位置
            text: 新对话文本
            popup: 新对话框样式
            figure: 新姿势ID
            position: 新位置
            transform: 新变换
            postures: 新姿势列表
            key_scenario: 新关键姿势
            emotion: 情感描述（用于姿势选择）
        """
        if not self.features.get('enable_dialog', False):
            debug_print(f"Page.update_dialog - enable_dialog is False")
            return
            
        try:
            if pos < 0 or pos >= len(self.interactions):
                debug_print(f"Page.update_dialog - pos: {pos} is out of interactions range")
                return
                
            interaction = self.interactions[pos]
            if interaction.type != "talk":
                return

            new_figure = figure

            # 更新文本和脚本
            if text is not None:
                interaction.content.text = MText(text)
                interaction.script.transcript = MText(text)
                interaction.script.alternative = MText(alternative_text) if alternative_text is not None else None
                interaction.script.reset2basename(self.actor)

                # 更新姿势
                if not (isinstance(new_figure, int) and new_figure > -1 and new_figure < len(CHARACTER_FIGURES[self.actor])):
                    if isinstance(postures, list) and len(postures) > 0:
                        new_figure = self.story._posture_selector.select_posture(
                            actor_name=self.actor, 
                            postures=postures, 
                            key_scenario=key_scenario)
                    else:
                        new_figure = self.story._posture_selector.get_posture(
                            actor_name=self.actor, 
                            text=MText(text).default_text, 
                            emotion=emotion)

            # 更新其他属性
            if popup is not None:
                interaction.content.popup = popup
            if new_figure is not None:
                interaction.figure = new_figure
            if position is not None:
                interaction.position = position
            if transform is not None:
                interaction.transform = transform
                
            # 管理交互
            self._manage_interactions(interaction, "update")
            
        except Exception as e:
            self._handle_error(e, "update_dialog")
            
    def remove_dialog(self, pos: int):
        """移除对话
        
        Args:
            pos: 对话位置
        """
        if not self.features.get('enable_dialog', False):
            return
            
        try:
            if pos < 0 or pos >= len(self.interactions):
                return
                
            interaction = self.interactions[pos]
            if interaction.type != "talk":
                return
                
            # 管理交互
            self._manage_interactions(interaction, "remove")
            
            # 移除互动
            self.interactions.pop(pos)
            
        except Exception as e:
            self._handle_error(e, "remove_dialog")
            
    def add_bullet(self, text: Union[str, dict], language: str = DEFAULT_LANGUAGE):
        """添加子弹
        
        Args:
            text: 子弹文本
            language: 语言代码
        """

        if not self.features.get('enable_html', False):
            return

        if self.board is None:
            self.board = Board(type=SCENE_NOTES)

        if self.board.type == SCENE_NOTES:
            if not isinstance(self.board.content, Content):
                self.board.content = Content()
                self.board.content.html = self.story.styles\
                    .get("scenarios", {})\
                    .get("notes", {})\
                    .get("htmlTemplate", None)
            self.board.content.add_bullet(text, language)
            exported_scripts = self.board.content.export_scripts()
            if isinstance(exported_scripts, list) and len(exported_scripts) > 0:
                if self.note_interaction is not None:
                    self.note_interaction.transcript = exported_scripts[0]["transcript"],
                    self.note_interaction.alternative = exported_scripts[0]["alternative"] if "alternative" in exported_scripts[0] else None,
                else:
                    self.note_interaction = Interaction(
                        actor_name=SCENARIO_ACTOR_NOTES,
                        content=Content(
                            html=self.story.styles.get("scenarios", {}).get("notes", {}).get("htmlTemplate", None)
                    ),
                    script=Script(
                        sound = f"voice-{uuid.uuid4()}.mp3",
                        transcript = exported_scripts[0]["transcript"],
                        alternative = exported_scripts[0]["alternative"] if "alternative" in exported_scripts[0] else None,
                        narrator = self.actor
                    )
                )

    def update_bullet(self, index: int, text: Union[str, dict], language: str = DEFAULT_LANGUAGE):
        """更新子弹
        
        Args:
            index: 子弹索引
            text: 子弹文本
            language: 语言代码
        """

        if not self.features.get('enable_html', False):
            return

        if self.board is None:
            return

        if self.board.type == SCENE_NOTES and isinstance(self.board.content, Content):
            self.board.content.update_bullet(index, text, language)

            exported_scripts = self.board.content.export_scripts()
            if isinstance(exported_scripts, list) and len(exported_scripts) > 0:
                self.note_interaction.transcript = exported_scripts[0]["transcript"],
                self.note_interaction.alternative = exported_scripts[0]["alternative"] if "alternative" in exported_scripts[0] else None,

                same_transcript_found = False
                for script in exported_scripts[1:]:
                    if MText(script["transcript"]).get_text(language) == MText(text).get_text(language):
                        same_transcript_found = True
                        break
                if not same_transcript_found:
                    self.mute_scripts.append(
                        Script(
                            transcript=MText(text, language)
                        )
                    )

    def remove_bullet(self, index: int):
        """移除子弹
        
        Args:
            index: 子弹索引
        """

        if not self.features.get('enable_html', False):
            return
        
        if self.board is None:
            return

        if self.board.type == SCENE_NOTES and isinstance(self.board.content, Content):
            self.board.content.remove_bullet(index)

    def set_ending_effect(self, enable: bool = True):
        """设置当前页面是否需要添加结束音效交互
        
        Args:
            enable: 是否启用结束音效
        """
        self.ending_effect = enable

    def set_title(self, title: Union[str, dict]):
        """设置标题
        
        Args:
            title: 标题
        """

        if not self.features.get('enable_title', False):
            return

        self.title = MText(title)

        title_updated = False
        for interaction in self.default_interactions:
            if isinstance(interaction, Interaction) and isinstance(interaction.content, Content) \
                 and interaction.content.popup == 6:
                interaction.content.text = self.title
                interaction.script.transcript = self.title
                title_updated = True
                break
        
        if not title_updated:
            self.default_interactions.append(
                Interaction(
                    content=Content(
                    popup=6,
                    text=self.title
                ),
                actor_name=SCENARIO_ACTOR_CONCENTRAK,
                type="talk",
                script=Script(transcript=self.title)
            )
        )

    def export(self, voice_offset: int = 0, page_id: float = 0.0, ending_voice_id=-999) -> Dict:
        """导出页面数据
        
        Args:
            voice_offset (int): 语音偏移量，用于计算语音索引
            page_id (float): 页面ID
            ending_voice_id (int): 结束语音ID
            
        Returns:
            Dict: 包含voices和events的字典
        """

        # 导出基础交互数据
        out_objects = ActorManager()
        out_transcripts = []
        out_interactions = []

        # 合并 PostureInteraction 到 Dialog 的 interactions
        posture_interaction_merged = False
        for i, interaction in enumerate(self.interactions):
            if isinstance(interaction, Interaction) and interaction.type == "talk" \
                and isinstance(interaction.content, Content) \
                    and isinstance(interaction.content.popup, int) \
                    and interaction.content.popup not in (-1, 2, 4, 6):
                for j, default_interaction in enumerate(self.default_interactions):
                    if isinstance(default_interaction, PostureInteraction):
                        if default_interaction.actor_name == interaction.actor_name:
                            self.interactions[i].figure = default_interaction.figure
                            self.interactions[i].position = default_interaction.position
                            self.interactions[i].transform = default_interaction.transform
                            self.default_interactions.pop(j)
                            posture_interaction_merged = True
                            debug_print(f"Page.export - merged posture interaction {j} into dialog interaction {i}")
                            break
                if posture_interaction_merged:
                    break

        page_voice_offset = voice_offset
        source_interactions = self.default_interactions + self.interactions
        # 如果 note_interaction 存在且有声音，则添加到 source_interactions，否则忽略
        if isinstance(self.note_interaction, Interaction) and isinstance(self.note_interaction.script, Script) \
            and self.note_interaction.script.sound and len(self.note_interaction.script.sound) > 0:
            source_interactions.append(self.note_interaction)
        for interaction in source_interactions:
            if hasattr(interaction, 'script') and isinstance(interaction.script, Script) \
                and interaction.script.sound and len(interaction.script.sound) > 0:
                voice_script = interaction.script.export()
                if voice_script is not None:
                    out_transcripts.append(voice_script)
                    interaction.content.voice = page_voice_offset
                    page_voice_offset += 1
                if self.has_image and interaction.content \
                    and interaction.content.popup not in [None, -1, 2, 4, 6]:
                        interaction.content.popup = 4
            if isinstance(interaction, Interaction):
                actor_id = out_objects.get_actor_id_or_add(interaction.actor_name)
                exported = interaction.export(actor_id)
                if exported is not None:
                    out_interactions.append(exported)
        
        # 导出旁白相关的语音数据（如果存在）
        if hasattr(self, 'narration_interactions'):
            narration_event, page_voice_offset, out_objects = self.export_narration(page_voice_offset, out_objects)
            out_transcripts.extend(narration_event.get('voices', []))
            out_interactions.extend(narration_event.get('interactions', []))

        # 导出问题相关的语音数据（如果存在）
        if hasattr(self, 'question_interactions'):
            question_event, page_voice_offset, out_objects = self.export_question(page_voice_offset, out_objects)
            out_transcripts.extend(question_event.get('voices', []))
            out_interactions.extend(question_event.get('interactions', []))
        
        # 添加结束音效
        if self.ending_effect:
            ending_interaction = Interaction(
                actor_name=SCENARIO_ACTOR_ENDING,
                content=Content(voice=ending_voice_id)
            )
            out_interactions.append(ending_interaction.export(out_objects.get_actor_id_or_add(SCENARIO_ACTOR_ENDING)))

        # 去除 out_interactions 中的 scripts
        for interaction in out_interactions:
            if isinstance(interaction, dict) and interaction.get("script"):
                interaction.pop("script")

        # 构建事件数据
        events = [{
            "id": page_id,
            "objects": out_objects.export(),
            "interactions": out_interactions
        }]

        return {
            "voices": out_transcripts,
            "events": events
        }

    def _export_sound(self, script: Script, local_directory: str, synthesizer: VoiceSynthesizer, cos_uploader: CosUploader, upload_to_cos: bool = True, incremental: bool = True):
        out_script = script.copy()
        if isinstance(out_script.sound, str) \
            and (os.path.basename(out_script.sound) == out_script.sound or not incremental) \
            and (not out_script.soundReady):
            try:
                file_name = os.path.basename(out_script.sound)
                character = out_script.narrator
                transcript_object = MText(out_script.transcript).export()
                alternative_object = MText(out_script.alternative).export()
                if isinstance(transcript_object, str):
                    transcript_str = alternative_object[DEFAULT_LANGUAGE] \
                        if isinstance(alternative_object, dict) \
                            and len(alternative_object.get(DEFAULT_LANGUAGE, '')) > 0 \
                        else (
                            alternative_object \
                                if isinstance(alternative_object, str) \
                                    and len(alternative_object) > 0 \
                                else transcript_object
                        )
                    debug_print(f"synthesize_file: character: {character}, transcript: {normalize_math_chars(remove_emojis(transcript_str))}, language: {DEFAULT_LANGUAGE}, local_directory: {local_directory}, file_name: {file_name}")
                    preprocessed_str = transcript_str
                    preprocessed_str = remove_emojis(preprocessed_str)
                    preprocessed_str = normalize_math_chars(preprocessed_str)
                    preprocessed_str = VoiceSynthesizer.correct_pronunciation(
                            preprocessed_str, 
                            DEFAULT_LANGUAGE, 
                            PRONUNCIATION_DICTIONARY.get(DEFAULT_LANGUAGE, {})) 
                    output_dict = synthesizer.synthesize_file(
                                character, 
                                preprocessed_str, 
                                DEFAULT_LANGUAGE, 
                                local_directory, 
                                file_name
                            )
                    debug_print(f"synthesizer output:", output_dict)
                    local_output_file_name = os.path.join(local_directory, file_name)

                    if cos_uploader != None and upload_to_cos:
                        cos_uploader.local2cos(local_output_file_name, self.story.story_id, self.story._audio_path)
                        out_script.sound = self.story._get_story_audio_path(file_name)
                    out_script.languages = None
                elif isinstance(transcript_object, dict):
                    processed_languages = []
                    for language in transcript_object:
                        transcript_str = alternative_object[language] \
                            if isinstance(alternative_object, dict) \
                                and len(alternative_object.get(language, '')) > 0 \
                            else (
                                alternative_object \
                                    if language == DEFAULT_LANGUAGE \
                                        and isinstance(alternative_object, str) \
                                        and len(alternative_object) > 0 \
                                    else transcript_object[language]
                            )
                        if language != DEFAULT_LANGUAGE:
                            file_name = file_name[:-3]+language+".mp3"
                        preprocessed_str = transcript_str
                        preprocessed_str = remove_emojis(preprocessed_str)
                        preprocessed_str = normalize_math_chars(preprocessed_str)
                        preprocessed_str = VoiceSynthesizer.correct_pronunciation(
                            preprocessed_str, 
                            language, 
                            PRONUNCIATION_DICTIONARY.get(language, {}))           
                        output_dict = synthesizer.synthesize_file(
                                        character, 
                                        preprocessed_str, 
                                        language, 
                                        local_directory, 
                                        file_name
                                    )
                        debug_print(f"synthesizer output:", output_dict)
                        local_output_file_name = os.path.join(local_directory, file_name)

                        if cos_uploader != None and upload_to_cos:
                            cos_uploader.local2cos(local_output_file_name, self.story.story_id, self.story._audio_path)
                            if language == DEFAULT_LANGUAGE:
                                out_script.sound = self.story._get_story_audio_path(file_name)
                            else:
                                processed_languages.append(language)
                    out_script.languages = processed_languages
            except Exception as e:
                error_print(f"Page._export_sound", f"- synthesize & upload failed for transcript:")
                error_print(f"{out_script.transcript.export() if isinstance(out_script.transcript, MText) else out_script.transcript}")
                error_print(e)
                return script

        return out_script

    def export_audios(self, local_output_path=LOCAL_DEFAULT_ROOT, synthesizer=None, cos_uploader=None, upload_to_cos=True, incremental=True):
        if self.story==None:
            error_print(f"export_audios:", "No story exists, return.")
            return
        local_directory = os.path.join(local_output_path, self.story.story_id)
        if not os.path.exists(local_directory):
            os.makedirs(local_directory)

        current_synthesizer = synthesizer if synthesizer!=None else self.story._synthesizer if self.story!=None else None
        if current_synthesizer == None:
            error_print(f"export_audios:", "No Synthesizer available, ignore synthesizing/uploading/export_audios.")
            return

        current_cos_uploader = cos_uploader if cos_uploader!=None else self.story._cos_uploader if self.story!=None else None
        if current_cos_uploader == None:
            error_print(f"export_audios:", "No COS uploader available, ignore uploading/export_audios.")
            return

        for i, interaction in enumerate(self.default_interactions):
            script = interaction.script
            if not isinstance(script, Script):
                continue
            debug_print(f"export_audios:", "default_interactions script: {script.transcript.export() if isinstance(script.transcript, MText) else script.transcript}")
            if isinstance(script, Script) and isinstance(script.sound, str) and len(script.sound) > 0:
                self.default_interactions[i].script = self._export_sound(
                    script=script, 
                    local_directory=local_directory, 
                    synthesizer=current_synthesizer, 
                    cos_uploader=current_cos_uploader, 
                    upload_to_cos=upload_to_cos, 
                    incremental=incremental)

        for i, interaction in enumerate(self.interactions):
            script = interaction.script
            if not isinstance(script, Script):
                continue
            debug_print(f"export_audios interactions script: {script.transcript.export() if isinstance(script.transcript, MText) else script.transcript}")
            if isinstance(script, Script) and isinstance(script.sound, str) and len(script.sound) > 0:
                self.interactions[i].script = self._export_sound(
                    script=script, 
                    local_directory=local_directory, 
                    synthesizer=current_synthesizer, 
                    cos_uploader=current_cos_uploader, 
                    upload_to_cos=upload_to_cos, 
                    incremental=incremental)

        script = self.note_interaction.script if self.note_interaction else None
        if isinstance(script, Script) and isinstance(script.sound, str) and len(script.sound) > 0:
            debug_print(f"export_audios note_interaction script: {script.transcript.export() if isinstance(script.transcript, MText) else script.transcript}")
            self.note_interaction.script = self._export_sound(
                                                script=script, 
                                                local_directory=local_directory, 
                                                synthesizer=current_synthesizer, 
                                                cos_uploader=current_cos_uploader, 
                                                upload_to_cos=upload_to_cos, 
                                                incremental=incremental)
        
        if isinstance(self.narration_interactions, list):
            for i, interaction in enumerate(self.narration_interactions):
                script = interaction.script
                if not isinstance(script, Script):
                    continue
                debug_print(f"export_audios narration_interactions script: {script.transcript.export() if isinstance(script.transcript, MText) else script.transcript}")
                if isinstance(script.sound, str) and len(script.sound) > 0:
                    self.narration_interactions[i].script = self._export_sound(
                        script=script, 
                        local_directory=local_directory, 
                        synthesizer=current_synthesizer, 
                        cos_uploader=current_cos_uploader, 
                        upload_to_cos=upload_to_cos, 
                        incremental=incremental)

        if isinstance(self.question_interactions, list):
            for i, interaction in enumerate(self.question_interactions):
                script = interaction.script
                if not isinstance(script, Script):
                    continue
                debug_print(f"export_audios question_interactions script: {script.transcript.export() if isinstance(script.transcript, MText) else script.transcript}")
                if isinstance(script.sound, str) and len(script.sound) > 0:
                    self.question_interactions[i].script = self._export_sound(
                        script=script, 
                        local_directory=local_directory, 
                        synthesizer=current_synthesizer, 
                        cos_uploader=current_cos_uploader, 
                        upload_to_cos=upload_to_cos, 
                        incremental=incremental)
        else:
            error_print(f"No synthesizer available, return.")

    def export_scripts(self):
        """导出脚本数据
        
        Returns:
            List[Dict]: 脚本数据列表
        """
        scripts = []
        for interaction in self.interactions + [self.note_interaction]:
            if hasattr(interaction, 'script') and isinstance(interaction.script, Script):
                scripts.append(interaction.script.export())
        
        if hasattr(self, 'narration_interactions'):
            scripts += self.export_narration_scripts()

        if hasattr(self, 'question_interactions'):
            scripts += self.export_question_scripts()
        
        # 导出有声音的脚本
        for script in self.mute_scripts + self.image_mute_scripts \
            + (self.board_content_list_scripts if hasattr(self, 'board_content_list_scripts') else []):
            scripts.append({
                "transcript": script.transcript.export()
            })
        
        return scripts

    def export_voices(self) -> List[Dict]:
        """导出语音数据"""
        voices = []
        for interaction in self.interactions + self.narration_interactions \
            + self.question_interactions + [self.note_interaction]:
            if isinstance(interaction, Interaction) \
                and interaction.script is not None and interaction.script.sound:
                # 确保保存完整的语音文件路径
                voices.append({
                    "sound": interaction.script.sound,  # 已经是完整路径
                    "languages": interaction.script.languages,
                    "transcript": interaction.script.transcript.export(),
                    "alternative": interaction.script.alternative.export() if interaction.script.alternative else None,
                    "narrator": interaction.script.narrator
                })
                if interaction.script.alternative:
                    voices[-1]["alternative"] = interaction.script.alternative.export()
        return voices
    
    def export_interactions(self) -> List[Dict]:
        """导出交互数据"""
        interactions = []
        for interaction in self.interactions + self.default_interactions \
            + self.narration_interactions + self.question_interactions + [self.note_interaction]:
            if isinstance(interaction, Interaction):
                interaction_data = interaction.export()
                if interaction_data:
                    interactions.append(interaction_data)   
        return interactions

    def test(self, file_name: str = "test_page.json", local_output_path: str = LOCAL_DEFAULT_ROOT, incremental: bool = True):
        """测试导出页面到文件
        
        Args:
            file_name: 输出文件名，默认"testPage.json"
            local_output_path: 本地输出目录，默认为LOCAL_DEFAULT_ROOT
            incremental: 是否使用增量导出，默认为True
        """
        if self.story is None:
            error_print(f"No story exists, return.")
            return

        self.export_audios(
            local_output_path=local_output_path, 
            synthesizer=self.story._synthesizer, 
            cos_uploader=self.story._cos_uploader, 
            upload_to_cos=True, 
            incremental=incremental
        )

        with open(os.path.join(local_output_path, file_name), "w") as file:
            json.dump(
                self.export(), file, ensure_ascii=False, indent=4, sort_keys=False
            )
        info_print(f"Page.test exported to {os.path.join(local_output_path, file_name)}")

    def _is_dialog_interaction(self, interaction: Dict) -> bool:
        # 必须是talk类型
        if interaction.get("type") != "talk":
            return False
            
        # actor必须在VISIBLE_ACTORS中
        actor_name = interaction.get("actor_name")
        if actor_name not in VISIBLE_ACTORS:
            return False
            
        # 不能是特殊用途的popup（2或6）
        content = interaction.get("content", {})
        if content.get("popup") in [2, 6]:
            return False
            
        return True

    def apply_characters_images(self, interactions, objects):
        if not isinstance(self.story._characters_images, dict) or len(self.story._characters_images) == 0:
            return interactions
        
        new_interactions = copy.deepcopy(interactions)
            
        try:
            # 创建角色名到位置的映射
            char_positions = {}
            for char_name in self.story._characters_images.keys():
                char_positions[char_name] = []
                # 在interactions列表中查找对应的交互
                for i, interaction_data in enumerate(new_interactions):
                    if (isinstance(interaction_data, dict) and 
                        isinstance(interaction_data.get("actor"), int) and 
                        isinstance(objects, list) and
                        -1 < interaction_data.get("actor") < len(objects) and
                        objects[interaction_data.get("actor")].get("name") == char_name and
                        interaction_data.get("position") is not None):
                        char_positions[char_name].append({
                            "position": interaction_data.get("position"),
                            "figure": interaction_data.get("figure"),
                            "start": interaction_data.get("start"),
                            "duration": interaction_data.get("duration"),
                            "type": interaction_data.get("type"),
                            "content": interaction_data.get("content")
                        })
                        new_interactions.pop(i)
            
            # 处理每个角色的图片
            for char_name, char_data in self.story._characters_images.items():
                if not isinstance(char_data, dict) or "figure" not in char_data:
                    continue
                    
                # 获取图片信息
                figures = char_data["figure"]
                if not isinstance(figures, list) or not figures:
                    continue
                                        
                for occurrence in char_positions[char_name]:
                    # 获取位置信息
                    position = occurrence.get("position", [0, 0])  # 默认位置为[0, 0]
                    figure_id = occurrence.get("figure", None)
                    if figure_id is None:
                        continue
                    
                    figure = figures[figure_id]
                    if not isinstance(figure, dict) or "source" not in figure or "size" not in figure:
                        continue
                            
                    # 获取图片源和尺寸
                    source = figure["source"]
                    size = figure["size"]

                    rect = [
                        position[0],  # x
                        position[1],  # y
                        size[0],  # width
                        size[1]  # height
                    ]
                    
                    # 添加图片
                    self.add_image(source, 
                                   rect, 
                                   caption=figure.get("caption", ""), # contentList 默认空字符串(TODO: 修复平台bug，空caption无法显示图片)
                                   auto_fit=False,
                                   upload_to_cos=False)
                
        except Exception as e:
            error_print(f"Page.apply_characters_images:", "error in _apply_character_images:", str(e))

        return new_interactions

    def export_transcripts_by_actors(self):
        transcripts = []
        for interaction in self.interactions:
            if isinstance(interaction, Interaction) and isinstance(interaction.script, Script) \
                and interaction.actor_name in VISIBLE_ACTORS and isinstance(interaction.figure, int) \
                    and interaction.script and isinstance(interaction.script.transcript, str | MText):
                transcripts.append(
                    {
                        "actor": interaction.actor_name,
                        "figure": interaction.figure \
                            if not isinstance(interaction.figure, int) \
                            else CHARACTER_FIGURES.get(interaction.actor_name, [])[interaction.figure],
                        "transcript": interaction.script.transcript.export() \
                            if isinstance(interaction.script.transcript, MText) \
                                else interaction.script.transcript
                    }
                )
        return transcripts
