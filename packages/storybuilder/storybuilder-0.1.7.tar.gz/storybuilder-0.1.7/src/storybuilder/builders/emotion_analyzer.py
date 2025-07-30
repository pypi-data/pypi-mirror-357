from typing import Dict, List, Tuple
import jieba
import re
from .emotion_mapper import EmotionMapper

class EmotionAnalyzer:
    def __init__(self, locale: str = "chinese"):
        self.emotion_mapper = EmotionMapper(locale)
        self._init_emotion_keywords()
        
    def _init_emotion_keywords(self):
        """初始化情感关键词映射"""
        self.emotion_keywords = {}
        # 为每个情感加载关键词和整体描述
        for emotion in self.emotion_mapper.descriptions.keys():
            keywords = set(self.emotion_mapper.get_sentiment_keywords(emotion))
            # 将整体描述中的词也添加到关键词中
            for sentiment in self.emotion_mapper.get_overall_sentiments(emotion):
                keywords.update(sentiment.split('/'))
            self.emotion_keywords[emotion] = keywords
    
    def analyze_text(self, text: str) -> Tuple[str, float]:
        """
        分析文本并返回最匹配的情感类型及其匹配度
        
        Args:
            text: 输入文本
            
        Returns:
            Tuple[str, float]: (情感类型, 匹配度)
        """
        # 对文本进行分词
        words = set(jieba.cut(text))
        
        # 计算每个情感的匹配度
        emotion_scores = {}
        for emotion, keywords in self.emotion_keywords.items():
            # 计算关键词匹配数量
            matched_words = words.intersection(keywords)
            # 计算匹配度（匹配词数/总关键词数）
            score = len(matched_words) / len(keywords) if keywords else 0
            emotion_scores[emotion] = score
        
        # 获取得分最高的情感
        best_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        return best_emotion
    
    def get_emotion_details(self, text: str) -> Dict:
        """
        获取文本的详细情感分析结果
        
        Args:
            text: 输入文本
            
        Returns:
            Dict: {
                'emotion': 情感类型,
                'score': 匹配度,
                'matched_keywords': 匹配的关键词,
                'description': 情感描述
            }
        """
        words = set(jieba.cut(text))
        emotion, score = self.analyze_text(text)
        
        matched_keywords = words.intersection(self.emotion_keywords[emotion])
        
        return {
            'emotion': emotion,
            'score': score,
            'matched_keywords': list(matched_keywords),
            'description': self.emotion_mapper.get_image_description(emotion)
        } 