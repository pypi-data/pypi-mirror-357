from typing import Union, Optional, Dict, Any
from ..core import MText, MList, MHTML
from ..utils.constants import DEFAULT_LANGUAGE, debug_print, error_print, BREAK_TIME
from ..utils.helpers import cover_html_text_with_color_style, extract_text_from_html

class Content:
    """内容模型，用于存储各种类型的内容数据"""
    
    def __init__(self, popup: int = None, voice: int = None, 
                 text: MText = None, textAlign: str = None,
                 image: MText = None, src: MText = None, videoType: str = None,
                 magnify: bool = None, caption: MText = None, 
                 fontSize: Union[str, int] = None, fontColor: str = None,
                 colsPerRow: int = None, border: str = None,
                 rect: list = None, question: MText = None,
                 options: MList = None, answer: Union[str, MList] = None,
                 html: MHTML = None, type: str = None):
        """初始化Content对象
        
        Args:
            popup: 弹出层级别
            voice: 语音编号
            text: 文本内容
            textAlign: 文本对齐方式
            image: 图片
            src: 资源路径
            videoType: 视频类型
            magnify: 是否放大
            caption: 标题
            fontSize: 字体大小
            fontColor: 字体颜色
            colsPerRow: 每行列数
            border: 边框样式
            rect: 矩形区域
            question: 问题
            options: 选项列表
            answer: 答案
            html: HTML内容
            type: 内容类型
        """
        self.popup = popup
        self.voice = voice
        self.text = MText(text) if text else None
        self.textAlign = textAlign
        self.image = MText(image) if image else None
        self.src = MText(src) if src else None
        self.videoType = videoType
        self.magnify = magnify
        self.caption = MText(caption) if caption else None
        self.fontSize = fontSize if (isinstance(fontSize, str) and fontSize.endswith("px")) else \
            str(fontSize)+"px" if isinstance(fontSize, int) else None
        self.fontColor = fontColor
        self.colsPerRow = colsPerRow
        self.border = border
        self.rect = rect[:4] if (isinstance(rect, list) and len(rect)>=4) else None
        self.question = MText(question) if question else None
        self.options = MList(options) if options else None
        self.answer = MList(answer) if answer else None
        self.type = type

        self._html_template = None  # HTML模板，在所有语言中保持唯一
        self._bullets = {DEFAULT_LANGUAGE: []}  # 多语言子弹点列表
        self.html = html # 含_html_template和bullets解析

    @property
    def html(self) -> Optional[MHTML]:
        """获取HTML内容"""
        return self._html
    
    @html.setter
    def html(self, value: Optional[Union[MHTML, str, dict]]):
        """设置HTML内容并解析"""
        if isinstance(value, (dict, str)):
            value = MHTML(value)
        self._html = value
        if value:
            self._parse_html()
    
    @property
    def html_template(self) -> Optional[str]:
        """获取HTML模板"""
        return self._html_template
    
    @html_template.setter
    def html_template(self, value: Optional[str]):
        """设置HTML模板"""
        self._html_template = value
    
    @property
    def bullets(self) -> list:
        """获取默认语言的子弹点列表"""
        return self._bullets.get(DEFAULT_LANGUAGE, [])
    
    @bullets.setter
    def bullets(self, value: Optional[list]):
        """设置默认语言的子弹点列表"""
        if isinstance(value, list):
            self._bullets[DEFAULT_LANGUAGE] = value
        else:
            self._bullets[DEFAULT_LANGUAGE] = []
    
    def get_bullets(self, language: str = DEFAULT_LANGUAGE) -> list:
        """获取指定语言的子弹点列表
        
        Args:
            language: 语言代码
            
        Returns:
            指定语言的子弹点列表
        """
        return self._bullets.get(language, [])
    
    def set_bullets(self, bullets: list, language: str = DEFAULT_LANGUAGE):
        """设置指定语言的子弹点列表
        
        Args:
            bullets: 子弹点列表
            language: 语言代码
        """
        if isinstance(bullets, list):
            self._bullets[language] = bullets
        else:
            self._bullets[language] = []
    
    def add_bullet(self, text: Union[str, dict], language: str = DEFAULT_LANGUAGE):
        """添加子弹
        
        Args:
            text: 子弹文本
            language: 语言代码
        """
        self._bullets[DEFAULT_LANGUAGE].append(text)
        if language != DEFAULT_LANGUAGE:
            if language not in self._bullets:
                self._bullets[language] = self._bullets[DEFAULT_LANGUAGE]
            else:
                self._bullets[language].append(text)

    def update_bullet(self, index: int, text: Union[str, dict], language: str = DEFAULT_LANGUAGE):
        """更新子弹
        
        Args:
            index: 子弹索引
            text: 子弹文本
            language: 语言代码
        """
        if language != DEFAULT_LANGUAGE:
            if language not in self._bullets:
                self._bullets[language] = self._bullets[DEFAULT_LANGUAGE]
        self._bullets[language][index] = text

    def remove_bullet(self, index: int):
        """删除子弹
        
        Args:
            index: 子弹索引
            language: 语言代码
        """
        if -1 < index < len(self._bullets[DEFAULT_LANGUAGE]):
            for language in self._bullets.keys():
                self._bullets[language].pop(index)

    def _parse_html(self):
        """解析HTML内容，提取子弹点和模板"""
        if not self._html:
            return
            
        try:

            # 使用默认语言（zh-CN）的内容作为模板
            debug_print(f"html_text", self._html, "type of", type(self._html))
            html_text = MHTML(self._html).export(DEFAULT_LANGUAGE)
            if not html_text:
                return

            # 查找最左边的 <li> 和最右边的 </li>
            start_idx = html_text.find("<li>")
            end_idx = html_text.rfind("</li>")
            
            if start_idx >= 0 and end_idx >= 0:
                # 保存HTML模板
                self._html_template = html_text[:start_idx] + "<li></li>" + html_text[end_idx + 5:]
                
                # 处理每种语言的子弹点
                if isinstance(self._html, MHTML):
                    languages = self._html._template._data.keys()
                else: # str
                    languages = [DEFAULT_LANGUAGE]

                for language in languages:
                    lang_html = self._html.export(language)
                    if lang_html:
                        # 提取当前语言的子弹点内容
                        bullets = []
                        current_pos = 0
                        while True:
                            li_start = lang_html.find("<li>", current_pos)
                            if li_start == -1:
                                break
                            li_end = lang_html.find("</li>", li_start)
                            if li_end == -1:
                                break
                            bullet_content = lang_html[li_start + 4:li_end]
                            bullets.append(bullet_content)
                            current_pos = li_end + 5
                    self._bullets[language] = bullets
            else:
                # 如果没有找到子弹点标记，将整个HTML作为模板
                self._html_template = html_text
                self._bullets = {}
                
        except Exception as e:
            error_print(f"parse_html:", "Error parsing HTML content:", str(e))
    
    def _combine_html(self, language: str = DEFAULT_LANGUAGE) -> Optional[str]:
        """组合HTML模板和指定语言的子弹点
        
        Args:
            language: 语言代码
            
        Returns:
            组合后的HTML内容
        """
        if not self._html_template:
            return None
            
        try:
            # 查找 <li> 和 </li> 的位置
            start_idx = self._html_template.find("<li>")
            end_idx = self._html_template.find("</li>")
            
            if start_idx >= 0 and end_idx >= 0:
                # 获取指定语言的子弹点
                bullets = self._bullets.get(language, [])
                # 组合HTML
                bullets_str = "</li><li>".join(bullets) if bullets else ""
                return (
                    self._html_template[:start_idx + 4] +  # 开始到 <li>
                    bullets_str +  # 子弹点内容
                    self._html_template[end_idx:]  # </li> 到结束
                )
            else:
                return self._html_template
        except Exception as e:
            error_print(f"combine_html:", "Error combining HTML content:", str(e))
            return self._html_template

    def copy(self) -> 'Content':
        """创建当前对象的深拷贝"""
        copied = Content(
            popup=self.popup,
            voice=self.voice,
            text=self.text if isinstance(self.text, str) else self.text.copy() if self.text else None,
            textAlign=self.textAlign,
            image=self.image.copy() if self.image else None,
            src=self.src.copy() if self.src else None,
            videoType=self.videoType,
            magnify=self.magnify,
            caption=self.caption.copy() if self.caption else None,
            fontSize=self.fontSize,
            fontColor=self.fontColor,
            colsPerRow=self.colsPerRow,
            border=self.border,
            rect=self.rect[:] if self.rect else None,
            question=self.question.copy() if self.question else None,
            options=self.options.copy() if self.options else None,
            answer=self.answer.copy() if self.answer else None,
            html=self.html,
            type=self.type
        )

        copied._html_template = self._html_template
        copied._bullets = {language: bullets.copy() for language, bullets in self._bullets.items()}
        return copied
    
    def export(self) -> Optional[Dict[str, Any]]:
        """导出内容数据
        
        Returns:
            Dict[str, Any]: 包含内容数据的字典，如果没有数据则返回 None
        """
        data = {}
        if self.popup is not None:
            data["popup"] = self.popup
        if self.voice is not None:
            data["voice"] = self.voice
        if self.text is not None and MText(self.text).export() is not None:
            data["text"] = MText(self.text).export()
        if self.textAlign is not None:
            data["textAlign"] = self.textAlign
        if self.image is not None and MText(self.image).export() is not None:
            data["image"] = MText(self.image).export()
        if self.src is not None and MText(self.src).export() is not None:
            data["src"] = MText(self.src).export()
        if self.videoType is not None:
            data["videoType"] = self.videoType
        if self.magnify is True:
            data["magnify"] = self.magnify
        if self.caption is not None and MText(self.caption).export() is not None:
            data["caption"] = MText(self.caption).export()
        if self.fontSize is not None:
            data["fontSize"] = self.fontSize
        if self.fontColor is not None:
            data["fontColor"] = self.fontColor
        if self.colsPerRow is not None:
            data["colsPerRow"] = self.colsPerRow
        if self.border is not None:
            data["border"] = self.border
        if self.rect is not None:
            data["rect"] = self.rect
        if self.question is not None and MText(self.question).export() is not None:
            data["question"] = MText(self.question).export()
        if self.options is not None and MList(self.options).export() is not None:
            data["options"] = MList(self.options).export()
        if self.answer is not None and MList(self.answer).export() is not None:
            data["answer"] = MList(self.answer).export()
            
        # 导出HTML内容
        if self._html is not None:
            # 如果是MHTML对象，使用其export方法
            if isinstance(self._html, MHTML):
                html_data = {}
                # 添加所有语言的内容
                for language in self._html._template._data.keys():
                    exported = self._html.export(language)
                    if exported is not None:
                        html_data[language] = exported
                        # html_data[language] = cover_html_text_with_color_style(exported, color="white")
                    
                # 如果有内容，根据语言数量决定导出格式
                if html_data:
                    if len(html_data) == 1:  # 只有一种语言时直接使用字符串
                        data["html"] = list(html_data.values())[0]
                    else:  # 多语言时使用字典格式
                        data["html"] = html_data
            else:
                # 如果是普通字符串，直接使用
                if self._html:
                    data["html"] = self._html
                    # data["html"] = cover_html_text_with_color_style(self._html, color="white")
        elif self._combine_html() is not None:
            html_data = {}
            if isinstance(self._bullets, dict) and len(self._bullets.keys()) == 1:
                data["html"] = self._combine_html()
            else:
                for language in self._bullets.keys():
                    html_data[language] = self._combine_html(language)
                data["html"] = html_data

        if self.type is not None:
            data["type"] = self.type
            
        return data if data else None
    
    def export_scripts(self) -> Optional[Dict[str, Any]]:
        """导出脚本数据"""
        data = []
        PLACEHOLDER = "{PLACE_HOLDER}"

        # 导出子弹点
        multi_language_combined_data = {}
        if self._html is not None:
            if isinstance(self._html, MHTML):
                for language in self._html._template._data.keys():
                    exported = self._html.export(language)
                    if exported is not None:
                        multi_language_combined_data[language] = \
                            extract_text_from_html(exported.replace("</li><li>", PLACEHOLDER))\
                                .replace(PLACEHOLDER, BREAK_TIME)
            else:
                multi_language_combined_data[DEFAULT_LANGUAGE] = \
                    extract_text_from_html(self._html.replace("</li><li>", PLACEHOLDER))\
                        .replace(PLACEHOLDER, BREAK_TIME)
        elif self._combine_html() is not None:
            if isinstance(self._bullets, dict) and len(self._bullets.keys()) == 1:
                multi_language_combined_data[DEFAULT_LANGUAGE] = \
                    extract_text_from_html(self._combine_html().replace("</li><li>", PLACEHOLDER))\
                        .replace(PLACEHOLDER, BREAK_TIME)
            else:
                for language in self._bullets.keys():
                    multi_language_combined_data[language] = \
                        extract_text_from_html(self._combine_html(language).replace("</li><li>", PLACEHOLDER))\
                            .replace(PLACEHOLDER, BREAK_TIME)

        data.append({
            "transcript": multi_language_combined_data,
            "alternative": None
        })

        for i, _ in enumerate(self.bullets):
            bullet_entry_data_dict = {}
            for language in self._bullets.keys():
                bullet_entry_data_dict[language] = self.get_bullets(language)[i] \
                    if len(self.get_bullets(language)) > i else self.get_bullets()[i]
            data.append({
                "transcript": bullet_entry_data_dict
            })

        if self.caption and MText(self.caption).export():
            data.append({
                "transcript": MText(self.caption).export()
            })
        
        return data
    
    @staticmethod
    def load(data: Optional[Dict[str, Any]]) -> Optional['Content']:
        """从数据加载内容对象
        
        Args:
            data: 内容数据
            
        Returns:
            Content: 内容对象，如果数据无效则返回 None
        """
        if not isinstance(data, dict):
            return None
            
        content = Content(
            popup=data.get("popup"),
            voice=data.get("voice"),
            text=MText(data["text"]) if data.get("text") else None,
            textAlign=data.get("textAlign"),
            image=MText(data["image"]) if data.get("image") else None,
            src=MText(data["src"]) if data.get("src") else None,
            videoType=data.get("videoType"),
            magnify=data.get("magnify"),
            caption=MText(data["caption"]) if data.get("caption") else None,
            fontSize=data.get("fontSize"),
            fontColor=data.get("fontColor"),
            colsPerRow=data.get("colsPerRow"),
            border=data.get("border"),
            rect=data.get("rect"),
            question=MText(data["question"]) if data.get("question") else None,
            options=MList(data["options"]) if data.get("options") else None,
            answer=MList(data["answer"]) if data.get("answer") else None,
            html=MHTML(data["html"]) if data.get("html") else None,
            type=data.get("type")
        )
        
        # 加载子弹点列表 - 移除 Script 相关代码，直接使用字符串列表
        if "bullets" in data:
            if isinstance(data["bullets"], dict):
                # 多语言格式
                for language, bullets in data["bullets"].items():
                    if isinstance(bullets, list):
                        content._bullets[language] = bullets
            elif isinstance(data["bullets"], list):
                # 单语言格式
                content._bullets[DEFAULT_LANGUAGE] = data["bullets"]
                    
        return content