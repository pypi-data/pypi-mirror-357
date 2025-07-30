from typing import Optional, Dict, Union, List
from ..core import MText
from ..utils.constants import DEFAULT_LANGUAGE
import os

class Script:
    """脚本模型，用于管理语音和文本内容
    
    音频文件命名约定：
    - 默认语言：<sound file name>.mp3
    - 其他语言：<sound file name>.<language code>.mp3
    
    音频文件状态判断：
    - 如果 sound 路径以 /story/audios/ 开头，表示该音频文件已准备好
    - 如果 sound 只是基础文件名（如 voice-xxx.mp3），表示需要生成音频
    - languages 列表中的语言表示这些语言版本的音频已准备好
    """
    
    def __init__(self, sound: Optional[str] = None, transcript: Union[str, dict, MText, None] = None,
                 narrator: Optional[str] = None, languages: Optional[Union[str, List[str], tuple]] = None,
                 alternative: Union[str, dict, MText, None] = None, soundReady: bool = False):
        """初始化脚本对象
        
        Args:
            sound: 音频文件路径
            transcript: 文本内容
            narrator: 旁白者
            languages: 已合成的非默认语言列表
            alternative: 替代文本
            soundReady: 音频是否已准备好
        """
        self._sound = sound
        self._transcript = MText(transcript) if transcript else None
        self._narrator = narrator
        self._languages = None
        self._alternative = MText(alternative) if alternative else None
        self._soundReady = soundReady
        
        # 设置语言列表
        self.languages = languages
        
    @property
    def sound(self) -> Optional[str]:
        """获取音频文件路径"""
        return self._sound
        
    @sound.setter
    def sound(self, value: Optional[str]):
        """设置音频文件路径"""
        self._sound = value
        
    @property
    def transcript(self) -> Optional[MText]:
        """获取文本内容"""
        return self._transcript
        
    @transcript.setter
    def transcript(self, value: Union[str, dict, MText, None]):
        """设置文本内容，会触发音频状态重置"""
        self._transcript = MText(value) if value is not None else None
        self._reset_audio_state()  # 文本内容改变时重置音频状态
        
    @property
    def narrator(self) -> Optional[str]:
        """获取旁白者"""
        return self._narrator
        
    @narrator.setter
    def narrator(self, value: Optional[str]):
        """设置旁白者，会触发音频状态重置"""
        self._narrator = value
        self._reset_audio_state()  # 旁白者改变时重置音频状态
        
    @property
    def alternative(self) -> Optional[MText]:
        """获取替代文本"""
        return self._alternative
        
    @alternative.setter
    def alternative(self, value: Union[str, dict, MText, None]):
        """设置替代文本"""
        self._alternative = MText(value) if value is not None else None
        
    @property
    def languages(self) -> Optional[List[str]]:
        """获取已合成的非默认语言列表"""
        return self._languages
        
    @languages.setter
    def languages(self, value: Optional[Union[str, List[str], tuple]]):
        """设置已合成的非默认语言列表
        
        Args:
            value: 语言列表或单个语言字符串
        """
        self._languages = None
        if value:
            if isinstance(value, (list, tuple)):
                # 过滤掉默认语言和无效值
                valid_langs = [lang for lang in value 
                             if isinstance(lang, str) and lang.strip() 
                             and lang != DEFAULT_LANGUAGE]
                self._languages = valid_langs if valid_langs else None
            elif isinstance(value, str) and value.strip() and value != DEFAULT_LANGUAGE:
                self._languages = [value]
        
    @property
    def soundReady(self) -> bool:
        """获取音频是否已准备好"""
        return self._soundReady or self.is_sound_ready()
        
    @soundReady.setter
    def soundReady(self, value: bool):
        """设置音频是否已准备好"""
        self._soundReady = value
        
    def is_sound_ready(self) -> bool:
        """检查音频文件是否已准备好
        
        Returns:
            bool: 如果音频文件路径以 /story/audios/ 开头，返回 True
        """
        return bool(self._sound and self._sound.startswith("/story/audios/"))
        
    def _reset_audio_state(self):
        """重置音频状态，当文本或旁白者改变时调用"""
        if self._sound and len(self._sound) > 0:
            self._sound = os.path.basename(self._sound)
        self._languages = None  # 清除合成的语言列表
        self._soundReady = False  # 重置音频准备状态
        
    def reset2basename(self, narrator=None):
        """重置音频文件名为基础名称，并可选择性地更新旁白者
        
        Args:
            narrator: 新的旁白者
        """
        if narrator:
            self.narrator = narrator  # 会触发 _reset_audio_state
        else:
            self._reset_audio_state()
            
    def copy(self):
        """创建当前对象的深拷贝"""
        return Script(
            sound=self._sound,
            transcript=self._transcript.copy() if hasattr(self._transcript, "copy") else self._transcript,
            narrator=self._narrator,
            languages=self._languages[:] if self._languages else None,
            alternative=self._alternative.copy() if hasattr(self._alternative, "copy") else self._alternative,
            soundReady=self._soundReady
        )

    def export(self) -> Optional[Dict]:
        """导出为字典格式
        
        Returns:
            Dict: 包含sound、transcript、narrator等信息的字典，如果transcript无效则返回None
        """
        if not self._transcript or self._transcript.export() is None:
            return None
            
        data = {
            "sound": self._sound,
            "transcript": self._transcript.export(),
            "narrator": self._narrator
        }
        
        # 添加可选字段
        if self._languages:
            data["languages"] = self._languages
            
        if self._alternative and self._alternative.export():
            data["alternative"] = self._alternative.export()
            
        if self._soundReady:
            data["soundReady"] = True
            
        return data