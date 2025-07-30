from .emotion_mapper import EmotionMapper
from typing import List
import random

class FacialEmotion:
    def __init__(self, emotion: str, locale: str = "chinese"):
        self.emotion = emotion
        self.emotion_mapper = EmotionMapper(locale)
        
    @property
    def description(self) -> str:
        """获取表情的图像描述"""
        return self.emotion_mapper.get_image_description(self.emotion)
        
    @property
    def sentiments(self) -> List[str]:
        """获取表情的情感描述列表"""
        return self.emotion_mapper.get_overall_sentiments(self.emotion)
        
    @property
    def keywords(self) -> List[str]:
        """获取表情的关键词列表"""
        return self.emotion_mapper.get_sentiment_keywords(self.emotion)
        
    def get_random_sentiment(self) -> str:
        """随机获取一个情感描述"""
        sentiments = self.sentiments
        return random.choice(sentiments) if sentiments else ""
        
    def get_random_keywords(self, count: int = 3) -> List[str]:
        """随机获取指定数量的关键词"""
        keywords = self.keywords
        if not keywords:
            return []
        return random.sample(keywords, min(count, len(keywords))) 