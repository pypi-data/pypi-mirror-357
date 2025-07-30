from ..utils.constants import (
    DEFAULT_LANGUAGE, LOCAL_DEFAULT_ROOT, ENDING_SOUND, RED, YELLOW, BLUE, RESET, 
    DEFAULT_NARRATOR, SCENE_BLACKBOARD, SCENE_NOTES, SCENE_CLASSROOM, SCENE_EXAM, 
    SCENE_COVER, SCENE_CONCENTRAK, DEBUG_MODE, VISIBLE_ACTORS,
    debug_print, info_print, warn_print, error_print
)
from ..utils.helpers import merge_dicts, get_actors
from ..config.profiles import STORY_SCENARIO_STYLES, CHARACTER_POSITIONS
from ..config.figures import CHARACTER_FIGURE_ACCESSORY_KEYS, CHARACTER_FIGURES
from .pages import Page, ScenarioPage, PageInitMode
from .posture_selector import PostureSelector
from ..core import MText

import copy
import json
import os
import random
import uuid
from typing import List, Optional

class Story:
    def __init__(self, title, story_id=None, style=None, locale=DEFAULT_LANGUAGE, narrator=DEFAULT_NARRATOR, uploader=None, synthesizer=None, test_styles=None):
        """初始化故事对象

        Args:
            title: 故事标题
            story_id: 故事ID，如果为None则自动生成
            style: 故事样式
            locale: 语言区域设置
            narrator: 默认旁白者
            uploader: COS上传器
            synthesizer: 语音合成器
            test_styles: 测试环境中使用的样式配置，如果提供则优先使用
        """
        self.title = title
        self._story_id = story_id if story_id else str(uuid.uuid4())
        self._style = style if style else "close_up"
        self._locale = locale
        self._narrator = narrator
        self._cos_uploader = uploader
        self._synthesizer = synthesizer
        self._pages = []
        self._characters_images = []
        
        # 重要的类属性
        self.styles = test_styles[self._style] if test_styles else STORY_SCENARIO_STYLES[self._style]
        self._posture_selector = PostureSelector()
        self._poster_path = 'test/posters/'
        self._audio_path = 'test/audios/'
        
        info_print(f"Create a new story title: {self.title}, Id: {self._story_id}")

    def create_page(self, page_type, **kwargs):
        """创建页面
        
        Args:
            page_type: 页面类型
            **kwargs: 其他参数，可包含：
                - source: 图片或视频源
                - rect: 矩形区域 [x, y, width, height]，默认为 [0,0,1,1]
                - sourceType: 源类型，如果为 'video' 则设置为视频
                - videoType: 视频类型
                - text: 初始对话文本
                - actor: 角色名称
        """
        # 创建页面实例
        page = ScenarioPage(
            page_type=page_type,
            story_instance=self,
            init_mode=PageInitMode.NEW,
            **kwargs
        )
        
        self._pages.append(page)
        return page

    def create_page_at(self, index, page_type, **kwargs):
        """在指定位置创建页面"""
        page = ScenarioPage(
            page_type=page_type,
            story_instance=self,
            init_mode=PageInitMode.NEW,
            **kwargs
        )

        self._pages.insert(index, page)
        return page
    
    def remove_page_at(self, index):
        """删除指定位置的页面"""
        if 0 <= index < len(self._pages):
            return self._pages.pop(index)
        return None

    def test(self, file_name="test_story.json", local_output_path=LOCAL_DEFAULT_ROOT, incremental=True):
        for page in self._pages:
            page.export_audios(
                local_output_path=local_output_path, 
                synthesizer=self._synthesizer, 
                cos_uploader=self._cos_uploader, 
                upload_to_cos=True, 
                incremental=incremental
            )

        output_object = self.export()
        with open(os.path.join(local_output_path, file_name), "w") as file:
            json.dump(
                output_object, file, ensure_ascii=False, indent=4, sort_keys=False
            )
        info_print(f"Story.test exported to {os.path.join(local_output_path, file_name)}")
    
    def export(self):
        """导出故事数据
        
        Returns:
            Dict: 包含 voices 和 events 的字典，voices[0] 始终是结束音效
        """
        # 初始化语音列表，结束音效必须在第一个位置
        voices = [{"sound": ENDING_SOUND}]
        events = []
        
        # 导出每个页面的数据
        for i, page in enumerate(self._pages):
            # 传入0作为ending_voice_id
            page_object = page.export(voice_offset=len(voices), page_id=float(len(events)), ending_voice_id=0)
            
            # 收集有效的语音数据
            page_voices = []
            for voice in page_object["voices"]:
                if isinstance(voice, dict):
                    # 确保语音有效
                    if voice.get("sound") or (isinstance(voice.get("transcript", None), (str, dict)) and len(voice["transcript"]) > 0):
                        page_voices.append({k: v for k, v in voice.items() if k in ("sound", "languages")})
            voices.extend(page_voices)
            
            # 收集事件数据
            events.extend(page_object["events"])
        
        return {
            "voices": voices,
            "events": events
        }

    def export_scripts(self):
        """导出所有脚本数据"""
        scripts = []
        for i, page in enumerate(self._pages):
            # 传入0作为ending_voice_id
            page_scripts = page.export_scripts()
            if page_scripts:
                scripts.append({
                    "page": i,
                    "scripts": page_scripts
                })
        return scripts
    
    def export_transcripts(self):
        """导出主角对话脚本数据"""
        transcripts = []
        for i, page in enumerate(self._pages):
            page_scripts = page.export_scripts()
            if isinstance(page_scripts, list):
                for script in page_scripts:
                    if script.get("narrator") in VISIBLE_ACTORS:
                        transcripts.append({k: v for k, v in script.items() \
                                            if k in ("narrator", "transcript")})
        return transcripts

    def export_transcripts_by_actors(self):
        """导出故事主角对话脚本数据
        
        Returns:
            List: 包含主角对话脚本数据
        """
        transcripts = []
        
        # 导出每个页面的数据
        for i, page in enumerate(self._pages):
            page_transcripts_by_actors_object = page.export_transcripts_by_actors()
            if isinstance(page_transcripts_by_actors_object, list) \
                and len(page_transcripts_by_actors_object) > 0:
                transcripts.append({"page": i, "transcripts": page_transcripts_by_actors_object})
        
        return transcripts

    def export_audios(self, local_output_path=LOCAL_DEFAULT_ROOT, upload_to_cos=True, incremental=True):
        for page in self._pages:
            page.export_audios(
                local_output_path=local_output_path, 
                synthesizer=self._synthesizer, 
                cos_uploader=self._cos_uploader, 
                upload_to_cos=upload_to_cos,
                incremental=incremental
            )

    def export_product(self, file_name=None, local_output_path='./prod', page_range=None, split_by_cover=False):
        """导出故事到生产环境
        
        Args:
            file_name: 输出文件名，如果为None则使用默认文件名
            local_output_path: 本地输出路径，默认为'./prod'
            page_range: 页面范围，格式为[start:end:step]，类似Python的slice对象。例如：
                - [0:5] 导出前5页
                - [1:10:2] 导出第1-10页中的奇数页
                - [-5:] 导出最后5页
                如果为None则导出所有页面
            split_by_cover: 是否按封面页分页，默认为False
        
        Returns:
            导出的故事对象，如果失败则返回None
        """
        if self._cos_uploader == None:
            error_print(f"export_product:", "Cos uploader is not available, exit.")
            return None

        if not os.path.exists(local_output_path):
            os.makedirs(local_output_path)

        try:
            sub_stories = []

            # 处理页面范围
            if page_range:
                if isinstance(page_range, str):
                    # 解析字符串格式的范围，例如 "0:5" 或 "1:10:2"
                    parts = page_range.split(':')
                    start = int(parts[0]) if parts[0] else None
                    end = int(parts[1]) if len(parts) > 1 and parts[1] else None
                    step = int(parts[2]) if len(parts) > 2 and parts[2] else 1
                    selected_pages = self._pages[start:end:step]
                elif isinstance(page_range, (list, tuple)) and len(page_range) in (2, 3):
                    # 处理列表/元组格式的范围，例如 [0,5] 或 [1,10,2]
                    start = page_range[0]
                    end = page_range[1] if len(page_range) > 1 else None
                    step = page_range[2] if len(page_range) > 2 else 1
                    selected_pages = self._pages[start:end:step]
                else:
                    error_print(f"export_product:", "Invalid page_range format")
                    return None
                sub_stories.append(selected_pages)
            elif split_by_cover:
                selected_pages = []
                for page in self._pages:
                    if page.page_type == SCENE_COVER and len(selected_pages) > 0:
                        sub_stories.append(selected_pages)
                        selected_pages = []
                    selected_pages.append(page)
                sub_stories.append(selected_pages)
            else:
                selected_pages = self._pages
                sub_stories.append(selected_pages)

            sub_story_objects = []
            info_print(f"Story.export_product - {len(sub_stories)} sub_stories to be exported.")
            for story_index, sub_story_pages in enumerate(sub_stories):
                # 创建临时的Story对象用于导出
                temp_story = copy.deepcopy(self)
                temp_story._pages = sub_story_pages
                story_object = temp_story.export()
            
                # Copy audios to product path
                for i, voice in enumerate(story_object["voices"]):
                    default_file_name = voice["sound"]
                    story_object["voices"][i]["sound"] = self._cos_uploader.test2product(default_file_name)
                    if isinstance(story_object["voices"][i].get("languages", None), list) and len(story_object["voices"][i]["languages"]) > 0:
                        for language in story_object["voices"][i]["languages"]:
                            lingual_file_name = default_file_name[:-3] + language + '.mp3'
                            self._cos_uploader.test2product(lingual_file_name)

                # Copy images to product path
                for j, event in enumerate(story_object["events"]):
                    if "board" in event and isinstance(event["board"], dict):
                        board = event["board"]
                        if isinstance(board.get("content", None), dict):
                            if isinstance(board["content"].get("image", None), str) \
                            and len(board["content"]["image"]) > 0:
                                story_object["events"][j]["board"]["content"]["image"] = self._cos_uploader.test2product(board["content"]["image"])
                            elif isinstance(board["content"].get("image", None), dict) \
                            and len(board["content"]["image"]) > 0:
                                for language in board["content"]["image"].keys():
                                    story_object["events"][j]["board"]["content"]["image"][language] = self._cos_uploader.test2product(board["content"]["image"][language])
                        if isinstance(board.get("contentList", None), list) \
                            and len(board["contentList"]) > 0:
                            for k, content_entry in enumerate(board["contentList"]):
                                if isinstance(content_entry.get("image", None), str) \
                                    and len(content_entry["image"]) > 0:
                                    story_object["events"][j]["board"]["contentList"][k]["image"] = self._cos_uploader.test2product(content_entry["image"])
                                elif isinstance(content_entry.get("image", None), dict) \
                                    and len(content_entry["image"]) > 0:
                                    for language in content_entry["image"].keys():
                                        story_object["events"][j]["board"]["contentList"][k]["image"][language] = self._cos_uploader.test2product(content_entry["image"][language])

                product_file_name = file_name if file_name != None else os.path.join(local_output_path, (self.title or self._story_id) + f".product.{story_index}.json")
                with open(product_file_name, "w") as file:
                    json.dump(
                        story_object, file, ensure_ascii=False, indent=4, sort_keys=False
                    )
                info_print(f"Story resource copied from test to production, product story generated as {product_file_name}")
                sub_story_objects.append(story_object)
            return sub_story_objects

        except Exception as e:
            error_print(f"Story.export_product - export failed, error:", e)
            return None

    @staticmethod
    def build_story_collection(outputName, storyList):
        storyCollection = {"collection": []}
        for story in storyList:
            storyTitle = story[:len(story)-5] if story.endswith(".json") else story
            storyCollection["collection"].append(storyTitle)
        with open(outputName, "w") as file:
            json.dump(
                storyCollection, file, ensure_ascii=False, indent=4, sort_keys=False
            )
    
    @staticmethod
    def load_from_file(file_name, locale=DEFAULT_LANGUAGE, story_id=None, **kwargs):
        story = None
        try:
            with open(file_name, 'r') as f:
                object = json.load(f)

            voices = object.get("voices", [])  # 使用 get 方法，默认为空列表
            events = object.get("events", [])  # 使用 get 方法，默认为空列表
            
            if story_id is None:
                # 从语音数据中获取故事ID
                if len(voices) > 1:
                    for i in range(1, len(voices)):
                        path_segments = voices[i].get("sound", "//").split("/")
                        if len(path_segments) >= 2:
                            folder = path_segments[-2]
                            if len(folder) == len(str(uuid.uuid4())):
                                story_id = folder
                                break
                
                if story_id is None:
                    story_id = str(uuid.uuid4())
                    warn_print(f"Story ID not found, generate a new one {story_id}.")
            info_print(f"Loading story from file {file_name}, Story ID: {story_id}")
                        
            story_style = None
            valid_scene = None
            
            # 从事件中获取有效场景和页面类型
            scene_found = False
            for i in range(len(events)):
                scene_data = events[i].get("scene", None)
                if scene_data is not None:
                    # 检查场景类型
                    if isinstance(scene_data, str):
                        valid_scene = scene_data
                    elif isinstance(scene_data, dict):
                        if scene_data.get("scene") is not None:
                            valid_scene = scene_data["scene"]
                        elif scene_data.get("index") is not None:
                            valid_scene = {"index": scene_data["index"], "bgColor": scene_data.get("bgColor", None)}
                            
                    # 根据场景定页面类型
                    for styleKey in STORY_SCENARIO_STYLES.keys():
                        for key, value in STORY_SCENARIO_STYLES[styleKey]["scenarios"].items():
                            # 检查是否匹配
                            if (isinstance(value, str) and value == valid_scene) or \
                               (isinstance(value, dict) and value.get("scene") == valid_scene) or \
                               (isinstance(value, dict) and isinstance(valid_scene, dict) and \
                                value.get("index") == valid_scene.get("index") and \
                                    value.get("bgColor") == valid_scene.get("bgColor")):
                                story_style = styleKey
                                scene_found = True
                                break
                        if scene_found:
                            break
                    if scene_found:
                        break
            
            debug_print(f"scene_found", "="*20, scene_found, "="*20, story_style if story_style is not None else "None", "="*20)
                    
            # 创建故事实例
            info_print(f"Loading story in original style of {story_style}")
            story = Story(
                title=os.path.splitext(os.path.basename(file_name))[0],
                story_id=story_id,
                style=story_style,
                locale=locale,
                **kwargs
            )
            
            story._load_characters_images(object.get("characters", {}))

            # 加载页面
            for event in events:
                debug_print(f"event_id", "="*20, event.get("id"), "="*20)

                page_type = None
                # 检查是否为笔记或考试场景
                board_data = event.get("board", None)
                if not page_type and isinstance(board_data, dict):
                    type_data = board_data.get("type", None)
                    if type_data in (SCENE_NOTES, SCENE_EXAM):
                        page_type = board_data.get("type")
                    content_data = board_data.get("content", None)
                    if not page_type:
                        if isinstance(content_data, dict):
                            if content_data.get("type") in (SCENE_NOTES, SCENE_EXAM):
                                page_type = content_data.get("type")
                        elif isinstance(content_data, list):
                            for content_entry in content_data:
                                if content_entry.get("type") in (SCENE_NOTES, SCENE_EXAM):
                                    page_type = content_entry.get("type")
                                    break
                    content_list_data = board_data.get("contentList", None)
                    if not page_type and isinstance(content_list_data, list):
                        for content_entry in content_list_data:
                            if content_entry.get("type") in (SCENE_NOTES, SCENE_EXAM):
                                page_type = content_entry.get("type")
                                break

                scene_data = event.get("scene", None)
                if isinstance(scene_data, dict):
                    if isinstance(scene_data, dict) and scene_data.get("index") == "0bd6c33e-31eb-4083-8dd8-ee07837bc975":
                        page_type = SCENE_CONCENTRAK
                    else:
                        for story_style in STORY_SCENARIO_STYLES:
                            for scene_key, scene_value in STORY_SCENARIO_STYLES[story_style]["scenarios"].items():
                                if isinstance(scene_data, dict):
                                    if isinstance(scene_value, dict) \
                                        and scene_value.get("bgColor") \
                                        and scene_value.get("bgColor") == scene_data.get("bgColor"):
                                        page_type = scene_key
                                        break
                                elif isinstance(scene_data, str):
                                    if isinstance(scene_value, dict):
                                        if scene_value.get("scene") == scene_data:
                                            page_type = scene_key
                                            break
                            if not page_type:
                                break
                
                if not page_type:
                    interactions_data = event.get("interactions", [])
                    if len(interactions_data) == 0:
                        page_type = SCENE_COVER
                    else:
                        objects_data = event.get("objects", [])
                        if len(objects_data) > 0 and len(interactions_data) > 0:
                            for interaction in interactions_data:
                                if isinstance(interaction, dict) and isinstance(interaction.get("actor"), int) \
                                    and interaction.get("actor") < len(objects_data):
                                    actor_name = objects_data[interaction.get("actor")]["name"]
                                    if actor_name in VISIBLE_ACTORS and interaction.get("figure", -1) > -1:
                                        page_type = SCENE_CLASSROOM
                                        break

                if not page_type:
                    interactions_data = event.get("interactions", [])
                    for interaction in interactions_data:
                        if isinstance(interaction, dict) \
                            and interaction.get("content", {}).get("type") == "talk" \
                            and interaction.get("content", {}).get("popup") == 6:
                            page_type = SCENE_CONCENTRAK
                            break

                debug_print(f"page_type", "="*20, page_type, "before", "="*20)

                if page_type is None:
                    page_type = SCENE_BLACKBOARD

                page = ScenarioPage(
                    story_instance=story,
                    init_mode=PageInitMode.LOAD,
                    page_type=page_type,
                    voices=voices,
                    scene=event.get("scene"),
                    board=event.get("board"),
                    objects=event.get("objects"),
                    interactions=event.get("interactions"),
                    duration=event.get("duration"),
                    transition=event.get("transition"),
                    **{k: v for k, v in event.items() \
                       if k not in ("scene", "board", "objects", "interactions", "duration", "transition")}
                )
                debug_print(f"page_type", "="*20, page_type, "created", "="*20)
                story._pages.append(page)
                
            return story
            
        except Exception as e:
            error_print("Load story from file exception:\n", str(e))
            return None

    @property
    def story_id(self):
        return self._story_id
        
    @property
    def style(self):
        return self._style
        
    @property
    def locale(self):
        return self._locale
        
    @property
    def narrator(self):
        return self._narrator
        
    @property
    def pages(self):
        return self._pages
    
    def _get_story_audio_path(self, file_name):
        return os.path.join("/", self._audio_path, self.story_id, file_name)

    def _get_posture_position(self, actor_name: str, figure_id: int, key_scenario: str):
        """获取角色姿势对应的位置
        
        Args:
            actor_name: 角色名称
            figure_id: 姿势ID
            key_scenario: 场景名称
            
        Returns:
            位置坐标 [x, y]
        """
        figure_name = CHARACTER_FIGURES[actor_name][figure_id]
        if any(keyword in figure_name for keyword in ["boy", "sports-boy"]):
            if "half" in figure_name:
                return self.styles["positions"]["right-bottom"]
            elif "standright" in figure_name:
                return self.styles["positions"]["right"]
            elif "-stand-" in figure_name:
                return self.styles["positions"]["left"]
            else:  # head
                return [0.5, 0.5]
        elif any(keyword in figure_name for keyword in ["girl"]): # girl or cue
            if "half" in figure_name or "half" in key_scenario:
                return self.styles["positions"]["right-bottom"]
            elif "standleft" in figure_name:
                return self.styles["positions"]["left"]
            elif "-stand-" in figure_name or actor_name == "cue":
                return self.styles["positions"]["right"]
            else:  # head
                return [0.5, 0.5]
        else:
            return [0, 0]

    def upload_image_to_cos(self, image_path: str, apply_hash: bool = True) -> str:
        """上传图片到 COS
        
        Args:
            image_path: 图片路径
            apply_hash: 是否应用哈希值，默认为 True
            
        Returns:
            str: 上传后的图片路径
        """
        if not self._cos_uploader:
            error_print(f"No COS uploader available, return original path.")
            return image_path
            
        try:
            return self._cos_uploader.local2cos(image_path, self._story_id, self._poster_path, apply_hash)
        except Exception as e:
            error_print(f"Upload image to COS failed:", str(e))
            return image_path

    def set_styls(self, styles_name: str):
        if styles_name not in STORY_SCENARIO_STYLES.keys():
            error_print("Story.set_styles", "- Incorrect styles name:", styles_name)
            return
        debug_print("Story.set_styles", "- styles_name:", styles_name)

        for page in self._pages:
            page.apply_style(STORY_SCENARIO_STYLES[styles_name])

        self._style = styles_name
        self.styles = STORY_SCENARIO_STYLES[styles_name]

    def _load_characters_images(self, characters):
        """加载characters中的图片。
        
        Args:
            characters: 包含角色图片信息的字典
            interactions: 包含位置信息的交互列表
        """
        if not characters or not isinstance(characters, dict):
            return
        
        self._characters_images = characters
