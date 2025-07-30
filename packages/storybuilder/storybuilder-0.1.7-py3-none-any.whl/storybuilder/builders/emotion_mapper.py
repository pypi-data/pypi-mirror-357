import json
import os
from typing import Dict, List, Optional

class EmotionMapper:
    def __init__(self, locale: str = "chinese"):
        self.locale = locale
        self._load_descriptions()
        
    def _load_descriptions(self):
        """加载情感描述文件"""
        json_path = os.path.join(
            os.path.dirname(__file__), 
            './sentiment_description.json'
        )
        with open(json_path, 'r', encoding='utf-8') as f:
            self.descriptions = json.load(f)
            
    def get_image_description(self, emotion: str) -> str:
        """获取表情的图像描述"""
        if emotion in self.descriptions:
            return self.descriptions[emotion]["image_description"]
        return ""
        
    def get_overall_sentiments(self, emotion: str) -> List[str]:
        """获取表情的整体情感描述"""
        if emotion in self.descriptions:
            return self.descriptions[emotion]["sentiments"][self.locale]["overall"]
        return []
        
    def get_sentiment_keywords(self, emotion: str) -> List[str]:
        """获取表情的关键词描述"""
        if emotion in self.descriptions:
            return self.descriptions[emotion]["sentiments"][self.locale]["keywords"]
        return []
        
    def get_all_descriptions(self, emotion: str) -> Dict:
        """获取表情的所有描述信息"""
        if emotion in self.descriptions:
            return self.descriptions[emotion]
        return {} 