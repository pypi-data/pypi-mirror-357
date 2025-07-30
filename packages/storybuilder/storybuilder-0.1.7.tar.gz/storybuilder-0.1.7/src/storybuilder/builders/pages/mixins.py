from typing import Optional, Dict, List, Union, Any, Tuple
from ...core import MText, MList
from ...models import Script, Content, Interaction, Board, ActorManager, ExamInitInteraction, ExamErrorInteraction, ExamSuccessInteraction
from ...utils.constants import (
    DEFAULT_LANGUAGE, RED, BLUE, YELLOW, 
    RESET, SCENARIO_ACTOR_EXAM, SCENE_EXAM, 
    debug_print, info_print, warn_print, error_print
)
from ...utils.helpers import is_valid_http_url, get_image_size, fit_rect, DEFAULT_SCREEN_HEIGHT
import uuid

class QuestionMixin:
    """问题功能混入类，提供问题相关的功能。
    
    该类提供了问题相关的基础功能，包括：
    - 问题初始化
    - 问题设置
    - 交互处理
    
    Attributes:
        question_interactions (List[Interaction]): 问题相关交互
        correct_answer_id (int): 正确答案ID
        default_object (str): 默认对象
    """
    
    def initialize_question(self) -> None:
        """初始化问题相关属性"""
        self.question_interactions = []  # 问题相关交互
        self.question_mute_scripts = []  # 所有静音脚本（选项、提示等）
        self.correct_answer_id = 0

    def set_question(self, question: Union[str, Dict[str, str]],
                    options: Optional[Union[List, Dict]] = None,
                   answers: Optional[Union[List, Dict]] = None,
                    **kwargs) -> None:
        """设置问题。
        
        Args:
            question: 问题文本，可以是字符串或多语言字典
            options: 选项列表，可以是列表或多语言字典
            answers: 答案列表，可以是列表或多语言字典
            **kwargs: 额外参数，可包含：
                - alternative_text: 替代文本（用于语音）
                - font_size: 字体大小
                - font_color: 字体颜色
                - cols_per_row: 每行列数
                - rect: 矩形区域
                - onErrorPrompt: 错误提示
                - onSuccessPrompt: 成功提示
                - alwaysTruePrompt: 总是正确提示
        """
    
        if not self.SCENE_FEATURES[self.page_type].get("enable_question", False):
            warn_print(f"set_question is only available in question-enabled pages")
            return
            
        try:
                # 1. 准备问题内容和样式
            self._prepare_question_content(question, options, answers, **kwargs)
                    
                # 2. 计算正确答案ID
            if options is not None and answers is not None:
                self._compute_answer_id(options, answers)
                    
                # 3. 准备交互
            self._prepare_interactions(question, options, **kwargs)

                # 4. 准备 Options 加入 Mute 脚本
            self._create_option_scripts(options)
                    
        except Exception as e:
            error_print(f"Error in QuestionMixin.set_question:", str(e))

    def _prepare_interactions(self, question: Union[str, Dict[str, str]],
                              options: Optional[Union[List, Dict]] = None,
                              **kwargs: Any) -> None:
        """准备问题相关的交互"""

        # 1. 更新初始交互
        new_init_interaction = None
        for interaction in self.question_interactions:
            if isinstance(interaction, ExamInitInteraction):
                new_init_interaction = interaction.copy()
                if interaction.script.transcript != question or \
                    interaction.script.alternative != kwargs.get("alternative_text", None):
                    new_init_interaction.content.text=MText(question)
                    new_init_interaction.script.transcript=MText(question)
                    new_init_interaction.script.narrator=self.actor if self.actor else self.narrator
                    new_init_interaction.script.alternative=MText(kwargs.get("alternative_text"))
                    new_init_interaction.script.reset2basename(self.actor if self.actor else self.narrator)
                    debug_print(f"_prepare_interactions", f"- new_init_interaction: {new_init_interaction.export()}")
                break

        if new_init_interaction is None:
            actor_name=SCENARIO_ACTOR_EXAM
            new_init_interaction = ExamInitInteraction(
                actor_name=actor_name,
                text=MText(question),
                voice=-1,
                script=Script(
                    sound=f"voice-{uuid.uuid4()}.mp3",
                    transcript=MText(question),
                    alternative=MText(kwargs.get("alternative_text")),
                    narrator=self.actor if self.actor else self.narrator
                )
            )
            debug_print(f"_prepare_interactions", f"- new_init_interaction: {new_init_interaction.export()}")
        self.question_interactions = [new_init_interaction]
        
        # 2. 如果有选项，添加错误和成功交互
        if options is not None:
            # 错误交互
            error_text = self._get_error_prompt(**kwargs)
            error_script = Script(
                transcript=MText(error_text)
            ) if error_text else None
            self.question_interactions.append(ExamErrorInteraction(
                actor_name=SCENARIO_ACTOR_EXAM,
                text=MText(error_text),
                script=error_script
            ))
            debug_print(f"_prepare_interactions", f"- error_interaction: {self.question_interactions[-1].export()}")

        # 3. 成功交互（如果有答案）
        if self.correct_answer_id > 0:
            success_text = kwargs.get("onSuccessPrompt")
            success_script = Script(
                    transcript=MText(success_text)
            ) if success_text else None
            self.question_interactions.append(ExamSuccessInteraction(
                onResult=self.correct_answer_id,
                text=MText(success_text),
                script=success_script
            ))
            debug_print(f"_prepare_interactions", f"- success_interaction: {self.question_interactions[-1].export()}")

    def load_question(self, data: Dict[str, Any], voices: List[Dict] = None, interactions: List[Dict] = None) -> None:
        """从数据加载问题，保持现有的声音文件ID和narrator"""
        if not self.features[self.page_type].get("enable_question", False):
            return
            
        try:
            # 1. 加载问题内容和样式
            self.board.content.question = MText(data.get("question"))
            self.board.content.options = MList(data.get("options", []))
            self.board.content.answer = MList(data.get("answer")) if data.get("answer") else None
            
            # 2. 加载样式
            for key in ["fontSize", "fontColor", "colsPerRow", "rect"]:
                if key in data:
                    setattr(self.board.content, key, data[key])
            
            # 3. 初始化容器
            self.question_transcript = None
            self.question_mute_scripts = []
            self.question_interactions = []
            
            # 4. 加载交互和对应的脚本
            if interactions:
                for interaction in interactions:
                    content = interaction.get("content", {})
                    on_result = interaction.get("onResult")
                    
                    if on_result in [-2, 0]:  # 初始交互
                        # 加载问题主脚本
                        voice_data = None
                        if voices and content.get("voice") is not None:
                            voice_data = voices[content["voice"]]
                        # 添加初始交互
                        self.question_interactions.append(ExamInitInteraction(
                            text=self.board.content.question,
                            voice=-1,
                            script=Script(
                                sound=voice_data.get("sound") if voice_data else f"voice-{uuid.uuid4()}.mp3",
                                transcript=MText(self.board.content.question),
                                narrator=self.actor if self.actor else voice_data.get("narrator", self.narrator),
                                languages=voice_data.get("languages")
                            )
                        ))
                        
                    elif on_result == -1:  # 错误交互
                        self.question_interactions.append(ExamErrorInteraction(
                            text=MText(content.get("text")),
                            voice=content.get("voice"),
                            script=Script(
                                transcript=MText(content.get("text"))
                            ) if content.get("text") else None
                        ))
                        
                    else:  # 成功交互
                        self.question_interactions.append(ExamSuccessInteraction(
                            onResult=on_result,
                            text=MText(content.get("text")) if content.get("text") else None,
                            voice=content.get("voice"),
                            script=Script(
                                transcript=MText(content.get("text"))
                            ) if content.get("text") else None
                        ))
            
            # 5. 加载选项脚本
            if self.board.content.options:
                options_list = MList(self.board.content.options)
                self.question_mute_scripts.extend([
                    Script(
                        transcript=MText(option)
                    )
                    for option in options_list
                ])
            
            # 6. 计算正确答案ID
            self._compute_answer_id(
                self.board.content.options,
                self.board.content.answer
            )
                
        except Exception as e:
            error_print(f"Error in load_question:", str(e))
        
    def _prepare_question_content(self, question: Union[str, Dict[str, str]],
                              options: Union[List, Dict] = None,
                              answers: Optional[Union[List, Dict]] = None,
                              **kwargs: Any) -> None:
        """准备问题内容和样式"""
        if not isinstance(self.board, Board):
            self.board = Board()
        self.board.type = SCENE_EXAM
        self.board.content = Content(
            question = MText(question),
            options = MList(options) if options else None,
            answer = MList(answers) if answers else None
        )
        self._apply_question_styles(**kwargs)

    def _apply_question_styles(self, **kwargs: Any) -> None:
        """应用问题样式设置"""
        style_mappings = {
            "fontSize": "fontSize",
            "fontColor": "fontColor",
            "colsPerRow": "colsPerRow",
            "textAlign": "textAlign"
        }

        for key, attr in style_mappings.items():
            if key in kwargs:
                setattr(self.board.content, attr, kwargs[key])
            elif hasattr(self.board.content, attr) and \
                getattr(self.board.content, attr) is None:
                setattr(self.board.content, attr, \
                        self.story.styles.get("scenarios", {}).get(SCENE_EXAM, {}).get(attr, None))
        
        if "rect" in kwargs:
            self.board.rect = kwargs["rect"]
        elif self.board.rect is None:
            self.board.rect = self.story.styles.get("scenarios", {}).get(SCENE_EXAM, {}).get("rect", None)

    def _prepare_question_scripts(self, question: Union[str, Dict[str, str]],
                              options: Union[List, Dict],
                              **kwargs: Any) -> None:
        """准备问题相关脚本"""
        self._update_question_transcript(question)
        self._create_option_scripts(options)
            
    def _update_question_transcript(self, transcript_text: Union[str, Dict[str, str]], keep_sound: bool = False) -> None:
        """更新问题脚本"""
        if self.question_transcript is None:
            self._create_question_transcript(transcript_text)
        elif self.question_transcript.transcript != transcript_text:
            self._refresh_question_transcript(transcript_text, False)
            
    def _create_question_transcript(self, transcript_text: Union[str, Dict[str, str]]) -> None:
        """创建问题脚本"""
        self.question_transcript = Script(
            sound=f"voice-{uuid.uuid4()}.mp3",
            transcript=MText(transcript_text),
            narrator=self.actor if self.actor is not None else self.narrator
        )
        
    def _refresh_question_transcript(self, transcript_text: Union[str, Dict[str, str]], keep_sound: bool = False) -> None:
        """刷新问题脚本"""
        self.question_transcript.transcript = MText(transcript_text)
        if not self.question_transcript.sound:
            self.question_transcript.sound = f"voice-{uuid.uuid4()}.mp3"
        self.question_transcript.reset2basename(
            self.actor if self.actor is not None else self.narrator
        )
            
    def _create_option_scripts(self, options: Union[List, Dict]) -> None:
        """创建选项脚本"""
        options_list = MList(options)
        for option in options_list.get_list(DEFAULT_LANGUAGE):
            self.question_mute_scripts.append(Script(
                transcript=MText(option)
            ))
            
    def _compute_answer_id(self, options: Union[List, Dict],
                        answers: Optional[Union[List, Dict]]) -> None:
        """计算正确答案ID"""
        self.correct_answer_id = 0
        if answers is not None:
            options_list = MList(options)
            answers_list = MList(answers)
            option_list = options_list.get_list(DEFAULT_LANGUAGE)
            answer_list = answers_list.get_list(DEFAULT_LANGUAGE)
            
            self.correct_answer_id = sum(
                2**i
                for i, option in enumerate(option_list)
                for answer in answer_list
                if answer == option
            )
            debug_print(f"_compute_answer_id - correct_answer_id: {self.correct_answer_id}")
        
    def _get_error_prompt(self, **kwargs: Any) -> Dict[str, str]:
        """获取错误提示文本"""
        if "alwaysTruePrompt" in kwargs:
            return kwargs["alwaysTruePrompt"]
        if "onErrorPrompt" in kwargs:
            return kwargs["onErrorPrompt"]
        return {DEFAULT_LANGUAGE: "再想想", "en-US": "Think again"}
        
    def remove_question(self) -> None:
        """移除问题及其相关资源（脚本、交互等）"""
        if not self.SCENE_FEATURES[self.page_type].get("enable_question", False):
            warn_print(f"set_question is only available in question-enabled pages")
            return
            
        try:
            if not hasattr(self, 'board') or self.board is None:
                return
                
            # 移除问题内容
            self.board.content.question = None
            self.board.content.options = None
            self.board.content.answer = None
            
            # 移除问题相关脚本
            self.question_mute_scripts = []
            
            # 移除问题相关交互
            self.question_interactions = []
            
            # 重置答案ID
            self.correct_answer_id = 0
            
        except Exception as e:
            error_print(f"Error in remove_question:", str(e))

    def export_question_scripts(self) -> List[Script]:
        """导出所有问题相关的脚本。
        
        Returns:
            List[Script]: 包含问题脚本和静音脚本的列表
        """
        scripts = []
        for interaction in self.question_interactions:
            if hasattr(interaction, 'script') and isinstance(interaction.script, Script) \
                and interaction.script.sound and len(interaction.script.sound) > 0:
                scripts.append(interaction.script.export())
        scripts.extend([script.export() for script in self.question_mute_scripts if script.transcript])
        return scripts

    def export_question(self, voice_offset: int = 0, objects: ActorManager = None) -> Tuple[Dict[str, List], int, ActorManager]:
        """导出问题相关数据。
        
        Args:
            voice_offset: 语音索引偏移量
            
        Returns:
            Dict: 包含问题相关的voices和interactions的字典
        """
            
        out_objects = objects
        if out_objects is None:
            out_objects = ActorManager()
        else:
            out_objects = objects.copy()
            
        # 导出交互
        question_voice_offset = voice_offset
        out_question_transcripts = []
        out_question_interactions = []
        for interaction in self.question_interactions:
            if isinstance(interaction.script, Script) and interaction.script.sound and len(interaction.script.sound) > 0:
                out_question_transcripts.append(interaction.script.export())
                interaction.content.voice = question_voice_offset
                question_voice_offset += 1

            if isinstance(interaction, Interaction):
                actor_id = out_objects.get_actor_id_or_add(interaction.actor_name)
                exported = interaction.export(actor_id)
                if exported:
                    out_question_interactions.append(exported)
        
        return {
            "voices": out_question_transcripts,
            "interactions": out_question_interactions
        }, question_voice_offset, out_objects

    def get_question_count(self) -> int:
        """获取问题相关脚本数量，用于计算voice_offset"""
        count = 0
        if self.question_transcript:
            count += 1
        count += len(self.question_mute_scripts)
        return count

class NarrationMixin:
    """旁白功能混入类，提供旁白相关的功能。"""
    
    def initialize_narration(self, narrator: Optional[str] = None) -> None:
        """初始化旁白相关属性"""
        self.narrator = narrator
        self.narration_interactions = []  # 旁白交互
    
    def _is_narration_interaction(self, interaction: Dict) -> bool:
        """判断是否为旁白交互。
        
        Args:
            interaction: 交互数据
            
        Returns:
            bool: 是否为旁白交互
        """
        # 情况1：页面没有actor时，由narrator说出
        if not self.actor and interaction.get("narrator") == self.narrator:
            return True
        
        # 情况2：页面有actor且图片被放大时的解说
        if (hasattr(self, 'board') and self.board and 
            self.board.content.image and self.board.content.magnify):
            return interaction.get("onPoster", 0) > 0  # 只用onPoster判断图片放大
            
        return False
    
    def add_narration(self, text: Union[str, Dict[str, str]],
                     alternative_text: Optional[str] = None,
                     narrator: Optional[str] = None,
                     **kwargs) -> None:
        """添加旁白。
        
        Args:
            text: 旁白文本，可以是字符串或多语言字典
            alternative_text: 旁白替代文本，可以是字符串或多语言字典
            **kwargs: 其他参数，可包含：
                - start: 开始时间
                - duration: 持续时间
                - onPoster: 图片索引（用于图片放大时的解说）
        """
        if not self.SCENE_FEATURES[self.page_type].get('enable_narration', False):
            warn_print(f"add_narration is only available in narration-enabled pages")
            return
            
        # 创建旁白脚本
        soundReady = False
        if kwargs.get("sound") is not None:
            sound = kwargs.get("sound")
            soundReady = True
        else:
            sound = f"voice-{uuid.uuid4()}.mp3"

        script = Script(
            sound=sound,
            transcript=MText(text),
            alternative=MText(alternative_text) if alternative_text is not None else None,
            narrator=narrator if narrator is not None else self.narrator,  # 旁白总是由narrator说出
            soundReady=soundReady
        )
        
        # 创建旁白交互
        interaction = Interaction(
            type="talk",
            content=Content(
                text=MText(text),
                popup=4,  # 旁白固定使用popup=4
                voice=-1
            ),
            actor_name=narrator if narrator is not None else self.narrator,
            start=kwargs.get("start"),
            duration=kwargs.get("duration"),
            script=script
        )
        
        # 如果是图片放大的解说，添加onPoster
        if kwargs.get("onPoster") is not None:
            interaction.onPoster = kwargs.get("onPoster")
            
        self.narration_interactions.append(interaction)

    def update_narration(self, pos: int, 
                        text: Optional[Union[str, Dict[str, str]]] = None,
                        alternative_text: Optional[str] = None,
                        narrator: Optional[str] = None,
                        **kwargs) -> None:
        """更新旁白。
        
        Args:
            pos: 旁白位置
            text: 新旁白文本
            alternative_text: 新旁白替代文本
            **kwargs: 其他参数，可包含：
                - start: 新开始时间
                - duration: 新持续时间
                - onPoster: 新图片索引
        """
        if not self.SCENE_FEATURES[self.page_type].get('enable_narration', False):
            return
            
        try:
            if pos < 0 or pos >= len(self.narration_interactions):
                return
                
            interaction = self.narration_interactions[pos]
            
            # 更新文本和脚本
            if text is not None:
                interaction.content.text = MText(text)
                interaction.script.transcript = MText(text)
                interaction.script.reset2basename(self.narrator if self.narrator else self.actor)
                interaction.script.alternative = MText(alternative_text) \
                    if alternative_text is not None else None
                    
            if narrator is not None:
                interaction.script.narrator = narrator
                interaction.actor_name = narrator
                    
            # 更新其他属性
            if kwargs.get("start") is not None:
                interaction.start = kwargs.get("start")
            if kwargs.get("duration") is not None:
                interaction.duration = kwargs.get("duration")
            if kwargs.get("onPoster") is not None:
                interaction.onPoster = kwargs.get("onPoster")

            # 更新声音文件
            if kwargs.get("sound") is not None:
                interaction.script.sound = kwargs.get("sound")
                interaction.script.soundReady = True
                
        except Exception as e:
            error_print(f"Error in update_narration:", str(e))

    def remove_narration(self, pos: Optional[int] = None) -> None:
        """移除旁白。
        
        Args:
            pos: 旁白位置，如果为None则移除所有旁白
        """
        if not self.SCENE_FEATURES[self.page_type].get('enable_narration', False):
            return
            
        try:
            if pos is None:
                return
            elif 0 <= pos < len(self.narration_interactions):
                # 移除指定位置的旁白
                self.narration_interactions.pop(pos)
                
        except Exception as e:
            error_print(f"Error in remove_narration:", str(e))

    def load_narration(self, voices: List[Dict], interactions: List[Dict]) -> None:
        """从数据加载旁白。
        
        Args:
            voices: 语音数据列表
            interactions: 交互数据列表
        """
        try:
            self.narration_interactions = []
            
            for interaction in interactions:
                # 使用_is_narration_interaction判断是否为旁白
                if self._is_narration_interaction(interaction):
                    content = interaction.get("content", {})
                    voice_idx = content.get("voice")
                    if voice_idx is not None and voice_idx < len(voices):
                        voice_data = voices[voice_idx]
                        # 加载交互
                        narration_interaction = Interaction(
                            type="talk",
                            actor_name=self.narrator,
                            content=Content(
                                text=MText(content.get("text")),
                                popup=4,
                                voice=-1
                            ),
                            start=interaction.get("start"),
                            duration=interaction.get("duration"),
                            onPoster=interaction.get("onPoster", None),
                            script=Script(
                                sound=voice_data.get("sound"),
                                transcript=MText(content.get("text")),
                                narrator=self.narrator,
                                languages=voice_data.get("languages")
                            )
                        )
                        narration_interaction.script.soundReady = True if isinstance(narration_interaction.script.sound, str) \
                          and narration_interaction.script.sound.startswith("/story/audios/") else False
                            
                        self.narration_interactions.append(narration_interaction)
                        
        except Exception as e:
            error_print(f"Error in load_narration:", str(e))

    def export_narration(self, voice_offset: int = 0, objects: ActorManager = None) -> Tuple[Dict[str, List], int, ActorManager]:
        """导出旁白数据。
        
        Args:
            voice_offset: 语音索引偏移量
            
        Returns:
            Dict[str, List]: 包含旁白的voices和interactions的字典
            int: 新的语音索引偏移量
            ActorManager: 包含旁白相关的actors
        """
        out_objects = objects
        if out_objects is None:
            out_objects = ActorManager()
        else:
            out_objects = objects.copy()

        voices = []
        interactions = []
        
        # 导出脚本
        narration_voice_offset = voice_offset
        
        # 导出交互
        for interaction in self.narration_interactions:
            if hasattr(interaction, 'script') and isinstance(interaction.script, Script) \
                and interaction.script.sound and len(interaction.script.sound) > 0:
                voice_script = interaction.script.export()
                if voice_script is not None:
                    voices.append(voice_script)
                    interaction.content.voice = narration_voice_offset
                    narration_voice_offset += 1
            if isinstance(interaction, Interaction):
                actor_id = out_objects.get_actor_id_or_add(interaction.actor_name)
                exported = interaction.export(actor_id)
                if exported is not None:
                    interactions.append(exported)
        
        return {
            "voices": voices,
            "interactions": interactions
        }, narration_voice_offset, out_objects

    def export_narration_scripts(self) -> List[Dict]:
        """导出旁白脚本"""
        scripts = []
        for interaction in self.narration_interactions:
            if hasattr(interaction, 'script') and isinstance(interaction.script, Script) \
                and interaction.script.sound and len(interaction.script.sound) > 0:
                scripts.append(interaction.script.export())
        return scripts
    

class ImageMixin:
    """图片功能混入类，提供图片相关的功能。"""

    BASE_LINE_POSITION = 0.675
    
    def initialize_image(self) -> None:
        """初始化图片相关属性"""
        self.image_mute_scripts = []  # 图片相关的静音脚本（标题等）
        self.has_image = False

    def _process_image_source(self, source: Union[str, Dict[str, str]], 
                            rect: List[float],
                            auto_fit: bool,
                            upload_to_cos: bool,
                            **kwargs) -> Tuple[MText, MText, List[float]]:
        """处理图片源和标题。
        
        Args:
            source: 图片路径或多语言图片路径字典
            rect: 矩形区域
            auto_fit: 是否自动调整大小
            upload_to_cos: 是否上传到COS
            **kwargs: 额外参数, 如：base_line，用于基线对齐图片
            
        Returns:
            Tuple[MText, MText]: 处理后的图片源和标题
        """
        m_source = MText(source)
        m_caption = MText(kwargs.get("caption", ""))
        new_rect = rect
        base_line = kwargs.get("base_line", False)  # rect[1]==.675 is recommended for base_line alignment
        
        # 处理URL和本地图片
        source_text = m_source.get_text(DEFAULT_LANGUAGE)

        if not is_valid_http_url(source_text) and \
            not source_text.startswith("/story/posters/"):
            width, height = get_image_size(source_text)
            if width <= 0 or height <= 0:
                raise ValueError("Invalid image dimensions")
            
            if auto_fit:
                new_rect = fit_rect(new_rect, width, height)

            if base_line:
                new_rect[1] = self.BASE_LINE_POSITION - \
                    (new_rect[3] if new_rect[3] < 1.0 else new_rect[3]/DEFAULT_SCREEN_HEIGHT)

            if upload_to_cos and self.story and self.story._cos_uploader:
                if isinstance(source, dict):
                    updated_paths = {}
                    for lang, path in source.items():
                        updated_paths[lang] = self.story.upload_image_to_cos(
                            path,
                            apply_hash=kwargs.get("applyHash")
                        )
                    m_source = MText(updated_paths)
                else:
                    m_source = MText(self.story.upload_image_to_cos(
                        source_text,
                        apply_hash=kwargs.get("applyHash")
                    ))
                    
        return m_source, m_caption, new_rect
    
    def set_image(self, 
                 source: Union[str, Dict[str, str]], 
                 rect: List[float] = None,
                 auto_fit: bool = True,
                 upload_to_cos: bool = True,
                 **kwargs) -> None:
        """设置主图片（board.content.image）
        
        Args:
            source: 图片路径或多语言图片路径字典
            rect: 矩形区域 [x, y, width, height]
            auto_fit: 是否自动调整大小
            upload_to_cos: 是否上传到COS
            **kwargs: 额外参数，可包含：
                - caption: 图片标题
                - magnify: 放大功能
                - fontColor: 字体颜色
                - fontSize: 字体大小
                - applyHash: 是否应用哈希值
        """
        if not self.SCENE_FEATURES[self.page_type].get('enable_image', False):
            warn_print(f"ImageMixin.set_image - image is not enabled for page type: {self.page_type}")
            return
            
        try:
            new_rect = rect
            new_auto_fit = auto_fit
            if new_rect is None:
                new_rect = [0, 0, 1.0, 1.0]
                new_auto_fit = False

            # 处理图片源和标题
            m_source, m_caption, new_rect = self._process_image_source(
                source, new_rect, new_auto_fit, upload_to_cos, **kwargs
            )

            if self.board is None:
                self.board = Board()

            if kwargs.get("videoType"):
                self.board.content.src = m_source
                self.board.content.videoType = kwargs.get("videoType")
            else:
                self.board.content.image = m_source
            
            # 更新board.content
            if not (hasattr(self.board, "rect") and self.board.rect == new_rect):
                self.board.content.rect = new_rect

            # 更新样式
            for key in ["magnify", "fontColor", "fontSize"]:
                if key in kwargs:
                    setattr(self.board.content, key, kwargs[key])
            
            # 处理标题
            if m_caption.default_text and m_caption.default_text != "":
                self.board.content.caption = m_caption
                # 添加标题到静音脚本
                self.image_mute_scripts.append(Script(
                    transcript=m_caption
                ))
                if self.board.content is None:
                    self.board.content.fontColor = "white"
            
            self.has_image = True
            
        except Exception as e:
            error_print(f"Error in set_image:", str(e))
    
    def add_image(self, 
                 source: Union[str, Dict[str, str]], 
                 rect: List[float] = None,
                 auto_fit: bool = True,
                 upload_to_cos: bool = True,
                 **kwargs) -> None:
        """添加图片到contentList
        
        Args:
            source: 图片路径或多语言图片路径字典
            rect: 矩形区域 [x, y, width, height]
            auto_fit: 是否自动调整大小
            upload_to_cos: 是否上传到COS
            **kwargs: 额外参数，可包含：
                - caption: 图片标题
                - magnify: 放大功能
                - fontColor: 字体颜色
                - fontSize: 字体大小
                - applyHash: 是否应用哈希值
        """
        if not self.SCENE_FEATURES[self.page_type].get('enable_image', False):
            return
            
        try:
            new_rect = rect
            new_auto_fit = auto_fit
            if new_rect is None:
                new_rect = [0, 0, 1.0, 1.0]
                new_auto_fit = False
            
            # 处理图片源和标题
            m_source, m_caption, new_rect = self._process_image_source(
                source, new_rect, new_auto_fit, upload_to_cos, **kwargs
            )
            
            # 创建Content对象
            if kwargs.get("videoType"):
                content = Content(
                    src=m_source,
                    rect=new_rect,
                    **{k: v for k, v in kwargs.items() if k in ['magnify', 'fontColor', 'fontSize']}
                )
            else:
                content = Content(
                    image=m_source,
                    rect=new_rect,
                    **{k: v for k, v in kwargs.items() if k in ['magnify', 'fontColor', 'fontSize']}
                )

            # 处理标题
            caption_text = m_caption.get_text(DEFAULT_LANGUAGE) if m_caption else ""
            content.caption = m_caption if m_caption else ""
            if len(caption_text) > 0:
                # 添加标题到静音脚本
                self.image_mute_scripts.append(Script(
                    transcript=m_caption
                ))
                if self.board.content is None:
                    self.board.content.fontColor = "white"

            
            # 初始化contentList
            if self.board is None:
                self.board = Board()
            if self.board.contentList is None:
                self.board.contentList = []
            self.board.contentList.append(content)
            self.has_image = True
            
        except Exception as e:
            error_print(f"Error in add_image:", kwargs, str(e))
    
    def update_image(self, pos: int,
                    source: Optional[Union[str, Dict[str, str]]] = None,
                    rect: Optional[List[float]] = None,
                    auto_fit: Optional[bool] = True,
                    upload_to_cos: bool = True,
                    **kwargs) -> None:
        """更新contentList中的图片
        
        Args:
            pos: 图片位置（0表示主图片）
            source: 新图片路径
            rect: 新矩形区域
            auto_fit: 是否自动调整大小
            **kwargs: 额外参数，与add_image相同
        """
        if not self.SCENE_FEATURES[self.page_type].get('enable_image', False):
            return
            
        try:
            new_rect = rect
            new_auto_fit = auto_fit

            if pos == 0:
                # 更新主图片
                if source is not None:
                    if new_rect is None:
                        new_rect = self.board.rect
                        new_auto_fit = False

                    self.set_image(source, new_rect, new_auto_fit, **kwargs)
                elif new_rect is not None or kwargs:
                    # 只更新属性
                    if new_rect:
                        self.board.rect = new_rect
                    for key in ["magnify", "fontColor", "fontSize", "caption"]:
                        if key in kwargs:
                            setattr(self.board.content, key, 
                                  MText(kwargs[key]) if key == "caption" else kwargs[key])
            elif isinstance(self.board.contentList, list) and pos <= len(self.board.contentList):
                content = self.board.contentList[pos-1]
                if source is not None:
                    m_source, m_caption, new_rect = self._process_image_source(
                        source, 
                        new_rect or content.rect,
                        new_auto_fit,
                        upload_to_cos,
                        **kwargs
                    )
                    content.image = m_source
                    if m_caption.default_text:
                        content.caption = m_caption
                        # 更新对应的静音脚本
                        if pos-1 < len(self.image_mute_scripts):
                            self.image_mute_scripts[pos-1].transcript = m_caption
                        if self.board.content is None:
                            self.board.content.fontColor = "white"

                # 更新其他属性
                if rect is not None:
                    content.rect = rect
                for key in ["magnify", "fontColor", "fontSize"]:
                    if key in kwargs:
                        setattr(content, key, kwargs[key])

        except Exception as e:
            error_print(f"Error in update_image:", str(e))
    
    def remove_image(self, pos: int) -> None:
        """移除图片。
        
        Args:
            pos: 图片位置（0表示主图片）
        """
        if not self.SCENE_FEATURES[self.page_type].get('enable_image', False):
            return
            
        try:
            if pos == 0:
                # 移除主图片
                self.board.content.image = None
                self.board.content.caption = None
                # 移除对应的静音脚本
                if self.image_mute_scripts:
                    self.image_mute_scripts.pop(0)
            elif isinstance(self.board.contentList, list) and pos <= len(self.board.contentList):
                # 移除contentList中的图片
                self.board.contentList.pop(pos-1)
                # 移除对应的静音脚本
                if pos-1 < len(self.image_mute_scripts):
                    self.image_mute_scripts.pop(pos-1)
            
            # 检查是否还有其他图片
            self.has_image = (self.board.content.image is not None or 
                            (isinstance(self.board.contentList, list) and 
                             any(content.image is not None 
                                 for content in self.board.contentList)))
                
        except Exception as e:
            error_print(f"Error in remove_image:", str(e))
    
    def load_image(self, data: Dict[str, Any]) -> None:
        """从数据加载图片。
        
        Args:
            data: 图片数据
        """
        try:
            # 加载主图片
            if "image" in data:
                self.board.content.image = MText(data["image"])
                if "caption" in data:
                    caption = MText(data["caption"])
                    self.board.content.caption = caption
                    self.image_mute_scripts.append(Script(
                        transcript=caption,
                        sound=None,
                        narrator=self.actor if self.actor is not None else self.narrator
                    ))
                for key in ["rect", "magnify", "fontColor", "fontSize"]:
                    if key in data:
                        setattr(self.board.content, key, data[key])
            
            # 加载contentList中的图片
            if "contentList" in data and isinstance(data["contentList"], list):
                self.board.contentList = []
                for content_data in data["contentList"]:
                    if "image" in content_data:
                        content = Content(
                            image=MText(content_data["image"]),
                            rect=content_data.get("rect", [0, 0, 1, 1])
                        )
                        if "caption" in content_data:
                            caption = MText(content_data["caption"])
                            content.caption = caption
                            self.image_mute_scripts.append(Script(
                                transcript=caption,
                                sound=None,
                                narrator=self.actor if self.actor is not None else self.narrator
                            ))
                        for key in ["magnify", "fontColor", "fontSize"]:
                            if key in content_data:
                                setattr(content, key, content_data[key])
                        self.board.contentList.append(content)
            
            # 更新图片状态
            self.has_image = (self.board.content.image is not None or 
                            (isinstance(self.board.contentList, list) and 
                             any(content.image is not None 
                                 for content in self.board.contentList)))
                
        except Exception as e:
            error_print(f"Error in load_image:", str(e))
    
    def get_image_count(self) -> int:
        """获取图片相关脚本数量"""
        return len(self.image_mute_scripts)

