from typing import Optional, Dict, List, Union, Any, TYPE_CHECKING
from .page import Page, PageInitMode
from .mixins import QuestionMixin
from ...core import MHTML, MText, MList
from ...models import Content, Scene, Script, Board, Actor, Interaction, PostureInteraction, ActorManager
from ...utils.constants import (
    VISIBLE_ACTORS, INVISIBLE_ACTORS, SCENARIO_ACTORS, 
    RED, BLUE, YELLOW, RESET, DEFAULT_LANGUAGE, ENDING_SOUND,
    SCENE_BLACKBOARD, SCENE_NOTES, SCENE_CLASSROOM, SCENE_EXAM, 
    SCENE_COVER, SCENE_CONCENTRAK,
    SCENARIO_ACTOR_EXAM, SCENARIO_ACTOR_NOTES, SCENARIO_ACTOR_CONCENTRAK, 
    debug_print, warn_print, error_print, info_print
)
from ...utils.helpers import get_actors, is_valid_http_url, get_image_size, update_visible_actor
import copy
import uuid

if TYPE_CHECKING:
    from ...builders.story import Story

class ScenarioPage(Page):
    """场景页面类，用于处理所有类型的场景"""
    
    # 场景特性配置
    SCENE_FEATURES = {
        SCENE_CLASSROOM: {
            "enable_actor": True,        # 启用角色
            "enable_dialog": True,       # 启用对话
            "enable_narration": True,    # 启用旁白
            "enable_image": True,        # 启用图片
            "enable_image_magnify": True, # 启用图片放大
            "enable_video": True,        # 启用视频
            "enable_question": False,    # 禁用问题
            "enable_html": True,         # 启用HTML
            "enable_bullet": False,      # 禁用要点
            "enable_title": False,       # 禁用标题
            "enable_auto_transition": True,  # 启用自动过渡
            "enable_default_duration": True  # 启用默认持续时间
        },
        SCENE_BLACKBOARD: {
            "enable_actor": True,
            "enable_dialog": True,
            "enable_narration": True,
            "enable_image": True,
            "enable_image_magnify": True,
            "enable_video": True,
            "enable_question": False,
            "enable_html": True,
            "enable_bullet": True,
            "enable_title": False,
            "enable_auto_transition": True,
            "enable_default_duration": True
        },
        SCENE_EXAM: {
            "enable_actor": True,
            "enable_dialog": True,
            "enable_narration": True,
            "enable_image": True,
            "enable_image_magnify": True,
            "enable_video": True,
            "enable_question": True,     # 启用问题功能
            "enable_html": True,
            "enable_bullet": True,
            "enable_title": False,
            "enable_auto_transition": False,  # 考试页面禁用自动过渡
            "enable_default_duration": False  # 考试页面禁用默认持续时间
        },
        SCENE_NOTES: {
            "enable_actor": True,
            "enable_dialog": True,
            "enable_narration": True,
            "enable_image": True,
            "enable_image_magnify": False,
            "enable_video": True,
            "enable_question": True,
            "enable_html": True,
            "enable_bullet": True,
            "enable_title": False,
            "enable_auto_transition": True,
            "enable_default_duration": True
        },
        SCENE_COVER: {
            "enable_actor": False,       # 封面页禁用大多数功能
            "enable_dialog": False,
            "enable_narration": True,
            "enable_image": True,
            "enable_image_magnify": False,
            "enable_video": False,
            "enable_question": False,
            "enable_html": False,
            "enable_bullet": False,
            "enable_title": False,
            "enable_auto_transition": True,
            "enable_default_duration": False  # 封面页禁用默认持续时间
        },
        SCENE_CONCENTRAK: {
            "enable_actor": False,
            "enable_dialog": False,
            "enable_narration": True,
            "enable_image": False,
            "enable_image_magnify": False,
            "enable_video": False,
            "enable_question": False,
            "enable_html": False,
            "enable_bullet": False,
            "enable_title": True,        # 只启用标题功能
            "enable_auto_transition": True,
            "enable_default_duration": False  # 专注页禁用默认持续时间
        }
    }
    
    def __init__(self, story_instance: 'Story', init_mode: PageInitMode = PageInitMode.NEW, page_type: Optional[str] = None, **kwargs):
        """初始化场景页面
        
        Args:
            page_type: 页面类型
            story_instance: Story实例
            init_mode: 初始化模式（NEW 或 LOAD）
            **kwargs: 额外参数
        """

        # 确保story_instance存在
        if not story_instance:
            raise ValueError("Story instance is required")
        
        # 调用父类的初始化方法
        super().__init__(story_instance)

        # 设置页面类型
        self.page_type = page_type \
            if page_type in self.SCENE_FEATURES else SCENE_BLACKBOARD

        # 初始化特性字典
        self.features = copy.deepcopy(self.SCENE_FEATURES[self.page_type])

        # 根据初始化模式选择初始化路径
        if init_mode == PageInitMode.NEW:                
            # 场景相关
            if self.page_type in story_instance.styles.get("scenarios", {}):
                self.scene = Scene.load(story_instance.styles["scenarios"][self.page_type])

            debug_print(f"ScenarioPage.__init__ - scene: {self.scene}", "page_type:", self.page_type)
            if self.scene is not None:
                debug_print(f"ScenarioPage.__init__ - scene exported: {self.scene.export()}")

            # 初始化板块
            if self.page_type in (SCENE_NOTES, SCENE_EXAM):
                self.board = Board(
                    type=self.page_type, 
                    rect=self.story.styles["scenarios"][self.page_type]["rect"],
                    content=Content(
                        html=self.story.styles["scenarios"][SCENE_NOTES]["htmlTemplate"] \
                            if self.page_type == SCENE_NOTES else None
                    )
                )
            else:
                self.board = Board()
            
        self._load_from_kwargs(**kwargs)

    def _load_interactions(self, interactions, voices, objects):
        """加载交互和语音数据
        
        Args:
            interactions: 交互数据列表
            voices: 语音数据列表
            objects: 对象数据列表
        """
        try:
            if not isinstance(interactions, list):
                debug_print(f"ScenarioPage._load_interactions - interactions is not a list")
                return
            
            debug_print(f"Existing note_interaction: {self.note_interaction.export() if self.note_interaction else 'None'}")
            new_interactions = copy.deepcopy(interactions)
            # 检查是否是图片角色，定义于"characters"对象中
            debug_print(f"ScenarioPage._load_interactions - check image characters")
            is_image_character = False
            temp_actor_name = None
            if isinstance(objects, list):
                for actor_object in objects:                    
                    temp_actor_name = actor_object["name"]
                    if isinstance(self.story._characters_images, dict) \
                        and temp_actor_name in self.story._characters_images.keys():
                        new_interactions = self.apply_characters_images(new_interactions, objects)
                        is_image_character = True
                        break
            else:
                debug_print(f"ScenarioPage._load_interactions - objects is not a list")
            
            if is_image_character:
                debug_print(f"ScenarioPage._load_interactions - {temp_actor_name} is image character")

            # 处理每个交互
            for index, interaction_data in enumerate(new_interactions):
                if not isinstance(interaction_data, dict):
                    debug_print(f"ScenarioPage._load_interactions[{index}] - interaction_data is not a dict")
                    continue

                # 获取基本属性
                interaction_type = interaction_data.get("type")
                content_data = interaction_data.get("content", {})
                
                # 检查是否是结束语音
                debug_print(f"ScenarioPage._load_interactions[{index}] - check ending voice")
                voice_index = content_data.get("voice")
                if isinstance(voices, list) \
                    and voice_index is not None \
                    and voice_index > 0 \
                    and voice_index < len(voices) \
                    and voices[voice_index].get("sound") == ENDING_SOUND:
                    self.ending_effect = True
                    continue
                
                # 从交互中获取角色信息
                debug_print(f"ScenarioPage._load_interactions[{index}] - load objects:", objects)
                actor_name = None
                actor_position = None
                if isinstance(objects, list) and isinstance(interaction_data.get("actor"), int) \
                    and -1 < interaction_data.get("actor") < len(objects):
                    actor_object = objects[interaction_data.get("actor")]
                    actor_name = "M" if actor_object.get("name") == "" else actor_object.get("name")
                    actor_position = actor_object.get("position", None)
                else:
                    warn_print(f"ScenarioPage._load_interactions[{index}] - actor_name is not found, interaction_data:", interaction_data,
                               "objects:", objects, "actor:", interaction_data.get("actor"), "actor_name:", actor_name)

                if actor_position is None:
                    actor_position = interaction_data.get("position")
                actor_figure = interaction_data.get("figure")
                debug_print(f"ScenarioPage._load_interactions[{index}] - actor_name:", actor_name, "actor_position:", actor_position, "actor_id:", interaction_data.get('actor'))                                        

                # 如果是有语音的交互，创建对应的脚本
                if voice_index is not None and voice_index > 0 and voice_index < len(voices):
                    debug_print(f"ScenarioPage._load_interactions[{index}] - load interaction with voice")
                    # 确定 narrator
                    identified_transcript = Script(
                        sound=voices[voice_index].get("sound"),
                        transcript=MText(content_data.get("text")),  # 从交互内容获取文本
                        narrator=self.narrator if actor_name == SCENARIO_ACTOR_CONCENTRAK \
                            else actor_name if actor_name in VISIBLE_ACTORS+INVISIBLE_ACTORS \
                                else self.actor, #当前页面actor（visible）配音
                        languages=voices[voice_index].get("languages")
                    )

                    # 如果当前页面是笔记页, 获取旁白信息，否则无法导出脚本信息
                    if self.page_type == SCENE_NOTES and actor_name == self.actor \
                        and isinstance(self.board.content, Content) \
                        and self.board.content.export_scripts():
                        identified_transcript.transcript = self.board.content.export_scripts()[0]["transcript"]
                        
                    identified_transcript.soundReady = True if isinstance(identified_transcript.sound, str) \
                          and identified_transcript.sound.startswith("/story/audios/") else False
                    
                    if actor_name == SCENARIO_ACTOR_NOTES:
                        if self.note_interaction:
                            if isinstance(identified_transcript.transcript, MText) \
                                and identified_transcript.transcript.default_text != "":
                                self.note_interaction.script = identified_transcript
                        else:
                            self.note_interaction = Interaction(
                                actor_name=SCENARIO_ACTOR_NOTES,
                                content=Content(),
                                script=identified_transcript
                            )
                    elif actor_name == SCENARIO_ACTOR_EXAM:
                        interaction_found = False
                        for existing_interaction in self.question_interactions:
                            if (existing_interaction.onResult == interaction_data.get("onResult")) \
                                or (isinstance(interaction_data.get("onResult"), list) \
                                    and existing_interaction.onResult in interaction_data.get("onResult")):
                                if not isinstance(existing_interaction.content, Content):
                                    existing_interaction.content = Content()
                                existing_interaction.content.popup=interaction_data.get("content", {}).get("popup")
                                existing_interaction.content.text=interaction_data.get("content", {}).get("text")
                                existing_interaction.actor_name=actor_name
                                existing_interaction.script=identified_transcript
                                interaction_found = True
                                break
                        if not interaction_found:
                            self.question_interactions.append(Interaction(
                                actor_name=actor_name,
                                start=interaction_data.get("start"), 
                                duration=interaction_data.get("duration"), 
                                content=Content(
                                    text=MText(content_data.get("text")),
                                    popup=content_data.get("popup"),
                                    voice=-1
                                ),
                                onResult=interaction_data.get("onResult"),
                                onPoster=interaction_data.get("onPoster"),
                                type=interaction_type,
                                script=identified_transcript
                            ))
                    else:
                        # 创建内容对象，保持与脚本的索引关系
                        content = Content(
                            text=MText(content_data.get("text")),
                            popup=content_data.get("popup"),
                            voice=-1
                        )
                        
                        # 创建交互对象
                        debug_print(f"ScenarioPage._load_interactions[{index}] - interaction_data.get(\"position\"):", interaction_data.get("position"))
                        interaction = Interaction(
                            type=interaction_type,
                            content=content,
                            actor_name=actor_name,
                            figure=actor_figure,
                            position=actor_position,
                            transform=interaction_data.get("transform"),
                            start=interaction_data.get("start"),
                            duration=interaction_data.get("duration"),
                            onResult=interaction_data.get("onResult"),
                            onPoster=interaction_data.get("onPoster"),
                            script=identified_transcript
                        )

                        if interaction_data.get("onPoster") \
                            or interaction_data.get("onResult") \
                                or actor_name not in VISIBLE_ACTORS:
                            self.narration_interactions.append(interaction)
                        else:
                            self.interactions.append(interaction)
                    
                else:
                    debug_print(f"ScenarioPage._load_interactions[{index}] - load interaction without voice")
                    # 4. 处理无语音的交互(如姿势)
                    if interaction_type == "motion":
                        interaction = PostureInteraction(
                            actor_name=actor_name,
                            figure=actor_figure,
                            position=actor_position,
                            transform=interaction_data.get("transform"),
                            start=interaction_data.get("start"),
                            duration=interaction_data.get("duration"),
                            onResult=interaction_data.get("onResult"),
                            onPoster=interaction_data.get("onPoster")
                        )
                        self.default_interactions.append(interaction)
                    elif interaction_type == "talk" and content_data.get("popup") == 6:
                        self.title = content_data.get("text", "")
                        self.default_interactions.append(
                            Interaction(
                                type="talk",
                                actor_name=SCENARIO_ACTOR_CONCENTRAK,
                                content=Content(
                                    text=MText(content_data.get("text", "")),
                                    popup=6
                                ),
                                script=Script(transcript=self.title)
                            )
                        )
                    else:
                        # 其他无语音交互
                        debug_print(f"ScenarioPage._load_interactions[{index}] - NOT RECOGNIZED interaction, content:", content_data)
                        content = Content(
                            text=MText(content_data.get("text", "")),
                            popup=content_data.get("popup")
                        )
                        interaction = Interaction(
                            type=interaction_type,
                            actor_name=actor_name,
                            content=content,
                            figure=actor_figure,
                            position=actor_position,
                            transform=interaction_data.get("transform"),
                            start=interaction_data.get("start"),
                            duration=interaction_data.get("duration"),
                            onResult=interaction_data.get("onResult"),
                            onPoster=interaction_data.get("onPoster")
                        )
                        self.default_interactions.append(interaction)

            debug_print(f"ScenarioPage._load_interactions - default interactions count:", len(self.default_interactions))
            debug_print(f"ScenarioPage._load_interactions - interactions count:", len(self.interactions))
        except Exception as e:
            self._handle_error(e, "_load_interactions")

    def _load_from_kwargs(self, **kwargs):
        """从kwargs加载数据"""
        debug_print(f"ScenarioPage._load_from_kwargs - kwargs:", kwargs)

        # 设置自动过渡
        if self.features["enable_auto_transition"]:
            self._transition = kwargs.get('transition')
            
        # 设置默认持续时间
        if self.features["enable_default_duration"]:
            self._duration = kwargs.get('duration')

        # 加载场景
        if kwargs.get("scene", None) is not None:
            debug_print(f"ScenarioPage._load_from_kwargs - scene:")
            self.scene = Scene.load(kwargs["scene"])

        # 加载板块
        if kwargs.get("board", None) is not None and kwargs.get("board", None) != {}:
            debug_print(f"ScenarioPage._load_from_kwargs - board:")
            board_data = kwargs["board"]
            if isinstance(board_data, dict):
                # 确保 rect 被正确设置
                if "rect" in board_data:
                    rect = board_data["rect"]
                    if isinstance(rect, list) and len(rect) >= 4:
                        board_data["rect"] = rect[:4]
                # 加载板块
                debug_print(f"ScenarioPage._load_from_kwargs - board_data:")
                self.board = Board.load(board_data)
                if board_data.get("type")  == SCENE_EXAM:
                    self.set_question(
                        answers=board_data["content"].get("answer"),
                        **board_data["content"]
                    )
                elif board_data.get("type") == SCENE_NOTES:
                    self.note_interaction = Interaction(
                        actor_name=SCENARIO_ACTOR_NOTES,
                        content=Content(),
                        script=Script(
                            transcript = self.board.content.export_scripts()[0]["transcript"] \
                                if isinstance(self.board.content, Content) \
                                else None,
                            alternative = self.board.content.export_scripts()[0]["alternative"] \
                                if isinstance(self.board.content, Content) \
                                else None,
                            narrator = self.actor
                        )
                    )
                    if isinstance(board_data.get("contentList"), list):
                        board_data["contentList"] = [Content.load(c) for c in board_data["contentList"]]

                # 检查是否有图片
                if self.board.content and self.board.content.image:
                    self.has_image = True
                elif self.board.contentList:
                    for content in self.board.contentList:
                        if content.image:
                            self.has_image = True
                            break
        
        # 加载对象
        if isinstance(kwargs.get("objects", None), list):
            debug_print(f"ScenarioPage._load_from_kwargs - objects:")
            # 加载主角
            actor, narrator, _ = get_actors(kwargs["objects"])
            if actor:
                self.actor = actor
            if narrator:
                self.narrator = narrator

        # 加载交互
        if isinstance(kwargs.get("interactions", None), list):
            debug_print(f"ScenarioPage._load_from_kwargs - interactions:")
            self._load_interactions(kwargs["interactions"], kwargs.get("voices", []), kwargs.get("objects", None))
        
        # 如果提供了 actor 和 text 参数，创建初始对话
        if isinstance(kwargs.get("actor", None), str) and kwargs.get("actor") in VISIBLE_ACTORS:
            debug_print(f"ScenarioPage._load_from_kwargs - actor:")
            # 设置主角
            self.set_actor(
                actor=kwargs["actor"],
                postures=kwargs.get("postures"),
                key_scenario=kwargs.get("key_scenario") \
                    if kwargs.get("key_scenario") is not None else \
                        "half" if self.page_type in (SCENE_EXAM, SCENE_NOTES) \
                            else "-stand-",
                exclude_accessories=kwargs.get("exclude_accessories")
            )
            
            if isinstance(kwargs.get("text", None), (str, dict)):
                # 添加对话
                self.add_dialog(
                    text=kwargs.get("text"),
                    alternative_text=kwargs.get("alternative_text")
                )

        # 加载图片或视频
        if isinstance(kwargs.get("source", None), (str, dict)):
            debug_print(f"ScenarioPage._load_from_kwargs - source:")
            self.set_image(**kwargs)

        # 加载问题
        if isinstance(kwargs.get("question", None), (str, dict)):
            debug_print(f"ScenarioPage._load_from_kwargs - question:")
            self.set_question(**kwargs)

        if self.page_type == SCENE_CONCENTRAK and isinstance(kwargs.get("title", None), (str, dict)):
            self.set_title(kwargs.get("title"))

    def _check_feature(self, feature: str) -> bool:
        """检查特性是否启用
        
        Args:
            feature: 特性名称
            
        Returns:
            特性是否启用
        """
        return self.features.get(feature, False)
        
    def _require_feature(self, feature: str, method_name: str) -> bool:
        """要求特性必须启用
        
        Args:
            feature: 特性名称
            method_name: 方法名称
            
        Returns:
            特性是否启用
        """
        if not self._check_feature(feature):
            warn_print(f"{method_name} requires {feature} to be enabled")
            return False
        return True
        
    def export(self, voice_offset: int = 0, page_id: float = 0.0, ending_voice_id=-999) -> Dict:
        """导出页面数据
        
        Args:
            voice_offset (int): 语音偏移量，用于计算语音索引
            page_id (float): 页面ID
            ending_voice_id (int): 结束语音ID
        Returns:
            Dict: 包含voices和events的字典
        """
        # 获取基类的导出数据
        base_data = super().export(voice_offset, page_id, ending_voice_id)
        
        # 添加场景特有的数据
        if base_data["events"]:
            event_data = base_data["events"][0]
            
            # 创建一个新的有序字典，按照指定顺序排列键
            ordered_event = {}
            
            # 按照约定顺序添加键值对
            key_order = ["id", "duration", "transition", "scene", "board", "objects", "interactions"]
            for key in key_order:
                if key == "id":
                    ordered_event[key] = event_data.get(key)
                elif key == "duration":
                    ordered_event[key] = self.duration if self.duration is not None else ""
                elif key == "transition":
                    ordered_event[key] = self.transition if self.transition is not None else "manual"
                elif key == "scene":
                    ordered_event[key] = self.scene.export() if isinstance(self.scene, Scene) else \
                        self.scene if isinstance(self.scene, str) else "#FFFFFF"
                elif key == "board" and self.board and self.board.export() != {}:
                    ordered_event[key] = self.board.export()
                elif key == "objects":
                    ordered_event[key] = event_data.get(key)
                elif key == "interactions":
                    ordered_event[key] = event_data.get(key)
            
            # 更新事件数据
            base_data["events"][0] = ordered_event

        return base_data
