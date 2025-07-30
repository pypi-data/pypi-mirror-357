from typing import Dict, List, Optional, Tuple, Union
# from sentence_transformers import SentenceTransformer
from ..config.figures import CHARACTER_FIGURES, CHARACTER_FIGURE_ACCESSORY_KEYS
from ..utils.helpers import warn_print
import numpy as np
import os
import random
os.environ["TOKENIZERS_PARALLELISM"] = "false"

class PostureSelector:
    """姿势选择器，基于对话文本选择合适的角色姿势"""
    
    def __init__(self):
        # self.model = SentenceTransformer('distiluse-base-multilingual-cased-v2')  # optional:  paraphrase-xlm-r-multilingual-v1
        
        # 表情分类和对应的情感
        self.facial_emotions = {
            'happy': ['laugh', 'blinkgrin', 'playful', 'blissful', 'happy'],
            'sad': ['worried', 'crying'],
            'neutral': ['neutral', 'questioning'],
            'embarrassed': ['embarrassed', 'shy'],
            'confident': ['smug'],
            'surprised': ['surprised']
        }
        
        # 手势分类
        self.arm_gestures = {
            'active': ['finger1up', 'fistup', 'thumbup', 'waving'],
            'neutral': ['straight', 'handonhip'],
            'open': ['open']
        }
        
        # 情感关键词映射到表情
        self.emotion_keywords = {
            'happy': {
                '开心': 1.5, '高兴': 1.3, '笑': 1.4, '喜欢': 1.2,
                '太好了': 1.6, '棒': 1.4, '哈哈': 1.8, '好玩': 1.3,
                '有趣': 1.4, '快乐': 1.5,
                '嗯': 0.8, '好': 0.8, '行': 0.8, '可以': 0.8
            },
            'sad': {
                '难过': 1.5, '伤心': 1.4, '哭': 1.6, '失望': 1.3,
                '可惜': 1.2, '唉': 1.4, '呜': 1.7, '不想': 1.3,
                '担心': 1.4, '害怕': 1.5
            },
            'neutral': {
                '嗯': 0.6, '这样': 0.6, '是吗': 0.6, '为什么': 0.8,
                '怎么': 0.8, '什么': 0.7, '原来': 0.7,
                '好': 0.5, '行': 0.5, '可以': 0.5
            },
            'embarrassed': {
                '害羞': 1.4, '不好意思': 1.5, '抱歉': 1.3,
                '对不起': 1.4, '那个': 1.2, '这个': 1.2,
                '尴尬': 1.5, '羞': 1.4
            },
            'confident': {
                '厉害': 1.4, '当然': 1.3, '看好了': 1.5,
                '简单': 1.3, '我来': 1.4, '交给我': 1.4,
                '放心': 1.3, '没问题': 1.4,
                '好的': 0.8, '明白': 0.8, '知道了': 0.8
            },
            'surprised': {
                '惊': 1.5, '啊': 1.3, '天啊': 1.6, '竟然': 1.4,
                '居然': 1.4, '不会吧': 1.5, '真的吗': 1.4,
                '哇': 1.5, '难以置信': 1.6,
                '哦': 0.8, '这样啊': 0.8, '是吗': 0.8
            }
        }
        
        # 标点符号增强器
        self.punctuation_enhancers = {
            '!': 1.4, '！': 1.4,
            '?': 1.3, '？': 1.3,
            '...': 1.2, '…': 1.2,
            '!!': 1.5, '！！': 1.5,
            '??': 1.4, '？？': 1.4,
            '.': 1.1, '。': 1.1
        }

    def _get_emotion_score(self, text: str) -> Dict[str, float]:
        """计算文本的情感分数"""
        scores = {emotion: 0.2 for emotion in self.facial_emotions.keys()}  # 给每个情感一个基础分
        
        # 1. 关键词匹配
        for emotion, keywords in self.emotion_keywords.items():
            for keyword, weight in keywords.items():
                if keyword in text:
                    scores[emotion] += weight
        
        # 2. 标点符号增强
        total_enhancement = 1.0
        for punct, weight in self.punctuation_enhancers.items():
            if punct in text:
                total_enhancement *= weight
        
        # 应用增强并添加随机波动
        for emotion in scores:
            scores[emotion] *= total_enhancement
            # 添加随机波动使表现更戏剧化
            scores[emotion] *= np.random.uniform(0.9, 1.2)
        
        return scores

    def _select_facial(self, emotion: str, last_facial: Optional[str] = None) -> str:
        """选择表情"""
        available_facials = self.facial_emotions[emotion]
        if last_facial in available_facials:
            available_facials = [f for f in available_facials if f != last_facial]
        return np.random.choice(available_facials)

    def _select_gesture(self, emotion: str, is_left: bool = True) -> str:
        """选择手势"""
        # 根据情感选择手势类型的概率
        gesture_weights = {
            'happy': {'active': 0.6, 'open': 0.3, 'neutral': 0.1},
            'sad': {'neutral': 0.7, 'open': 0.3, 'active': 0.0},
            'neutral': {'neutral': 0.6, 'active': 0.2, 'open': 0.2},
            'embarrassed': {'neutral': 0.5, 'open': 0.3, 'active': 0.2},
            'confident': {'active': 0.7, 'neutral': 0.2, 'open': 0.1},
            'surprised': {'open': 0.6, 'neutral': 0.2, 'active': 0.2}
        }
        
        weights = gesture_weights[emotion]
        gesture_type = np.random.choice(list(weights.keys()), p=list(weights.values()))
        return np.random.choice(self.arm_gestures[gesture_type])

    def _get_available_postures(self, actor_name: str, emotion: str, key_scenario: Optional[str] = None) -> List[Tuple[int, str]]:
        """获取角色可用的姿势列表"""
        if actor_name not in CHARACTER_FIGURES:
            return []
            
        available_postures = CHARACTER_FIGURES[actor_name]
        
        # 如果指定了关键场景，从中选择
        if key_scenario:
            filtered = [(id, p) for id, p in enumerate(available_postures) if key_scenario in p]
        else:
            filtered = [(id, p) for id, p in enumerate(available_postures)]
        
        emotion_facials = self.facial_emotions[emotion]
        
        # 过滤出包含对应情感表情的姿势
        return [entry for entry in filtered if any(facial in entry[1] for facial in emotion_facials)]

    def _score_posture(self, posture: str, emotion: str, gesture_weights: Dict[str, float]) -> float:
        """计算姿势的得分"""
        score = 0.0
        
        # 表情得分
        for facial in self.facial_emotions[emotion]:
            if facial in posture:
                score += 1.0
                break
        
        # 手势得分
        for gesture_type, weight in gesture_weights.items():
            for gesture in self.arm_gestures[gesture_type]:
                if gesture in posture:
                    score += weight
        
        return score

    def get_posture(self, actor_name: str, text: Union[str, dict], emotion: Optional[str] = None, last_figure: Optional[int] = -1, key_scenario: Optional[str] = None) -> str:
        """通过情感分析模型选择角色姿势"""

        emotion_str = text
        if emotion is not None and len(emotion) > 0:
            emotion_str = emotion + ": " + emotion_str

        emotion_scores = self._get_emotion_score(emotion_str)
        
        # 如果所有情感分数都很低，随机增强一个情感
        max_score = max(emotion_scores.values())
        if max_score < 0.5:  # 分数阈值
            emotion = np.random.choice(list(emotion_scores.keys()))
            emotion_scores[emotion] *= 2.0  # 随机增强
        
        # 按分数排序的情感列表
        emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 为每个情感尝试选择姿势
        for emotion, score in emotions:
            available_postures = self._get_available_postures(actor_name, emotion, key_scenario)
            if not available_postures:
                continue
            
            # 移除上一个姿势（如果有）
            if last_figure > -1 and last_figure < len(available_postures):
                for i, p in enumerate(available_postures):
                    if p[0] == last_figure:
                        available_postures.remove(p)
                        break
            
            if not available_postures:  # 如果移除后没有可用姿势，继续下一个情感
                continue
            
            # 获取手势权重（更倾向于活跃的手势）
            gesture_weights = {
                'active': 0.7,  # 增加活跃手势的权重
                'neutral': 0.2,
                'open': 0.5     # 增加开放手势的权重
            }
            
            # 计算姿势得分时添加随机因素
            posture_scores = [
                (p[0], self._score_posture(p[1], emotion, gesture_weights) * np.random.uniform(0.9, 1.3))
                for p in available_postures
            ]
            
            # 从得分最高的三个姿势中随机选择一个
            top_n = min(3, len(posture_scores))
            top_postures = sorted(posture_scores, key=lambda x: x[1], reverse=True)[:top_n]
            return int(np.random.choice([p[0] for p in top_postures]))
        
        # 如果没有找到合适的姿势，随机选择一个非中性的姿势
        default_postures = [(id, p) for id, p in enumerate(CHARACTER_FIGURES.get(actor_name, []))
                          if not any(n in p for n in ['neutral', 'normal', 'calm'])]
        return int(np.random.choice([p[0] for p in default_postures]) if default_postures else -1)

    def get_all_scores(self, text: str) -> Dict[str, float]:
        """获取所有情感分数（用于调试）"""
        return self._get_emotion_score(text)

    def get_available_emotions(self, actor_name: str, key_scenario: Optional[str] = None) -> Dict[str, List[str]]:
        """获取角色可用的情感和对应的姿势（用于调试）"""
        result = {}
        for emotion in self.facial_emotions:
            postures = self._get_available_postures(actor_name, emotion, key_scenario)
            if postures:
                result[emotion] = [p[1] for p in postures]
        return result

    @staticmethod
    def select_posture(actor_name: str, postures: Optional[List[str]] = None, 
                      key_scenario: Optional[str] = None, exclude_accessories: bool = True) -> int:
        """选择角色姿势
        
        Args:
            actor_name: 角色名称
            postures: 指定的姿势列表
            key_scenario: 关键场景
            exclude_accessories: 是否排除配件
            
        Returns:
            str: 选择的姿势名称
        """
        if actor_name not in CHARACTER_FIGURES:
            return -1
        
        available_postures = [(id, p) for id, p in enumerate(CHARACTER_FIGURES[actor_name])]
        if exclude_accessories:
            # 检查postures参数中是否指定了某个配件
            required_accessories = set()
            if postures:
                for posture_filter in postures:
                    for accessory in CHARACTER_FIGURE_ACCESSORY_KEYS:
                        if accessory in posture_filter:
                            required_accessories.add(accessory)
            
            # 过滤逻辑：如果指定了配件，保留包含该配件的角色；否则排除所有配件
            if required_accessories:
                # 保留包含指定配件的角色，或者不包含任何配件的角色
                available_postures = [
                    figure for figure in available_postures 
                    if any(accessory in figure[1] for accessory in required_accessories) or 
                       not any(accessory in figure[1] for accessory in CHARACTER_FIGURE_ACCESSORY_KEYS)
                ]
            else:
                # 原始逻辑：排除所有包含配件的角色
                available_postures = [
                    figure for figure in available_postures 
                    if not any(accessory in figure[1] for accessory in CHARACTER_FIGURE_ACCESSORY_KEYS)
                ]

        filters = [key_scenario] + postures
        if filters:
            filtered = []
            while (len(filters) > 0 and len(filtered) == 0):
                filtered = [(id, p) for id, p in available_postures if all(filter in p for filter in filters)]
                filters.pop(-1)
    
            if len(filtered) == 0:
                warn_print(f"{actor_name} posture not found by {[key_scenario] + postures}")
                return 0
            else:
                available_postures = filtered

        # 默认返回任意一个可用姿势的id，而不是姿势名
        return random.choice(available_postures)[0]
