from typing import List, Dict, Optional, Union
import copy
import re

from ..utils.constants import BULLET_KEY, BREAK_TIME, DEFAULT_LANGUAGE
from ..utils.helpers import extract_html_elements
from .mtext import MText

class MHTML:
    """HTML内容处理类，支持多语言模板和元素的处理"""
    
    def __init__(self, template: Union[str, Dict[str, str], MText] = None, 
                 textList: List[Dict[str, str]] = None,
                 language: str = None):
        """初始化MHTML对象"""
        self._template = MText(template, language) if template else None
        self.bullets = {}  # 多语言列表项
        self.elements = {}  # 多语言元素
        
        if isinstance(textList, list):
            for textObject in textList:
                if isinstance(textObject, dict):
                    key = next(iter(textObject), None)
                    if key == BULLET_KEY and textObject[key].strip():  # 只添加非空列表项
                        self._add_bullet_to_lang(textObject[key], language or DEFAULT_LANGUAGE)
                    elif key is not None and textObject[key].strip():  # 只添加非空元素
                        self._add_element_to_lang(key, textObject[key], language or DEFAULT_LANGUAGE)

    def _add_bullet_to_lang(self, text: str, language: str) -> None:
        """添加指定语言的列表项"""
        if language not in self.bullets:
            self.bullets[language] = []
        if isinstance(text, str) and text.strip():
            self.bullets[language].append(text.strip())

    def _add_element_to_lang(self, tag: str, text: str, language: str) -> None:
        """添加指定语言的元素"""
        if language not in self.elements:
            self.elements[language] = []
        if isinstance(text, str) and text.strip():
            self.elements[language].append({tag: text.strip()})

    def copy(self) -> 'MHTML':
        """创建当前对象的深拷贝"""
        result = MHTML()
        result._template = self._template.copy() if self._template else None
        result.bullets = copy.deepcopy(self.bullets)
        result.elements = copy.deepcopy(self.elements)
        return result

    def export(self, language: str = DEFAULT_LANGUAGE) -> Optional[str]:
        """导出指定语言的HTML内容"""
        if not self._template:
            return None
            
        lang = language or DEFAULT_LANGUAGE
        template = self._template.get_text(lang)
        if not template:
            return None
            
        result = template
        
        # 处理元素
        if lang in self.elements:
            for entry in self.elements[lang]:
                key = next(iter(entry), None)
                if key is not None:
                    result = result.replace("{"+key+"}", entry[key], 1)
                    
        # 处理列表项
        if lang in self.bullets and self.bullets[lang]:
            # 构建列表项HTML
            bullet_items = []
            for item in self.bullets[lang]:
                bullet_items.append(f"<li>{item}</li>")
            bullet_html = "".join(bullet_items)
            # 替换{bullet}标签
            result = result.replace("{bullet}", bullet_html)
        else:
            # 没有列表项时，替换为空字符串
            result = result.replace("{bullet}", "")
            
        return result

    def export_all(self) -> Dict[str, str]:
        """导出所有语言版本的HTML内容"""
        result = {}
        languages = set()
        
        # 收集所有语言
        if self._template:
            languages.update(self._template._data.keys())
        languages.update(self.elements.keys())
        languages.update(self.bullets.keys())
        
        # 导出每种语言的内容
        for lang in languages:
            if content := self.export(lang):
                result[lang] = content
                
        return result
    
    def export_scripts(self) -> str:
        """导出脚本内容"""
        if not self._template:
            return None
        
        template = self._template
        if isinstance(template, MText):
            template = template.get_text(DEFAULT_LANGUAGE)
        
        if not template:
            return None
        
        resultList = []
        
        # 处理元素 - 只收集值，避免重复
        if DEFAULT_LANGUAGE in self.elements:
            values = set()  # 使用集合去重
            for entry in self.elements[DEFAULT_LANGUAGE]:
                value = next(iter(entry.values()), None)
                if value is not None and value not in values:
                    resultList.append(value)
                    values.add(value)
        
        # 处理列表项
        if DEFAULT_LANGUAGE in self.bullets and self.bullets[DEFAULT_LANGUAGE]:
            resultList.extend(self.bullets[DEFAULT_LANGUAGE])
        
        return BREAK_TIME.join(filter(None, resultList)) if resultList else None

    def set_template(self, template: Union[str, Dict[str, str], MText], language: str = None) -> None:
        """设置HTML模板"""
        self._template = MText(template, language)

    def add_element(self, tag: str, text: Union[str, Dict[str, str], MText], language: str = None) -> None:
        """添加元素
        
        Args:
            tag: 元素标签
            text: 元素内容，可以是字符串、语言字典或MText对象
            language: 指定语言代码，仅在text为字符串时使用
        """
        if isinstance(text, (str, dict, MText)):
            mtext = MText(text, language)
            for lang, content in mtext._data.items():
                self._add_element_to_lang(tag, content, lang)

    def add_bullet(self, text: Union[str, Dict[str, str], MText], language: str = None) -> None:
        """添加列表项
        
        Args:
            text: 列表项内容，可以是字符串、语言字典或MText对象
            language: 指定语言代码，仅在text为字符串时使用
        """
        if isinstance(text, (str, dict, MText)):
            mtext = MText(text, language)
            for lang, content in mtext._data.items():
                self._add_bullet_to_lang(content, lang)

    @staticmethod
    def load_from_text(htmlText: Union[str, Dict[str, str]], language: str = None) -> 'MHTML':
        """从HTML文本加载对象
        
        Args:
            htmlText: HTML文本字符串或语言字典
            language: 指定语言代码，仅在htmlText为字符串时使用
            
        Returns:
            MHTML对象
        """
        if isinstance(htmlText, dict):
            result = MHTML()
            for lang, text in htmlText.items():
                if isinstance(text, str):
                    result._template = MText(text, lang)  # 直接使用原始文本作为模板
                    # 从模板中提取占位符
                    pattern = r"\{([a-zA-Z0-9_]+)\}"
                    matches = re.finditer(pattern, text)
                    for match in matches:
                        key = match.group(1)
                        if key == "bullet":
                            continue  # 跳过bullet标签，它是特殊处理的
                        result._add_element_to_lang(key, "", lang)  # 添加空内容的元素
            return result
        elif isinstance(htmlText, str):
            result = MHTML()
            result._template = MText(htmlText, language)  # 直接使用原始文本作为模板
            # 从模板中提取占位符
            pattern = r"\{([a-zA-Z0-9_]+)\}"
            matches = re.finditer(pattern, htmlText)
            for match in matches:
                key = match.group(1)
                if key == "bullet":
                    continue  # 跳过bullet标签，它是特殊处理的
                result._add_element_to_lang(key, "", language)  # 添加空内容的元素
            return result
        return MHTML()