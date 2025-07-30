from typing import Optional, Dict, List
import os
import uuid

from ..models import Script
from ..utils.constants import (
    DEFAULT_LANGUAGE,
    debug_print, info_print, warn_print, error_print
)
from ..config.profiles import CHARACTER_VOICE_PROFILES
from .speech import Synthesizer

class VoiceSynthesizer:
    """语音构建器，用于处理语音合成相关功能"""
    
    def __init__(self, 
                 azure_subscription: Optional[str] = None,
                 azure_region: Optional[str] = None,
                 voice_profiles: Optional[Dict] = None):
        """初始化VoiceSynthesizer对象
        
        Args:
            azure_subscription: Azure语音服务订阅密钥
            azure_region: Azure服务区域
            voice_profiles: 角色语音配置
        """
        self.scripts = []
        self.current_narrator = None
        self.current_language = DEFAULT_LANGUAGE
        
        # Azure语音服务配置
        self.subscription = azure_subscription or os.environ.get('AZURE_SPEECH_KEY')
        self.region = azure_region or os.environ.get('AZURE_SPEECH_REGION')
        self.voice_profiles = voice_profiles or CHARACTER_VOICE_PROFILES
        
    def _new_audio_filename(self, language: Optional[str] = None) -> str:
        """生成新的音频文件名
        
        Args:
            language: 语言代码
            
        Returns:
            音频文件名
        """
        if language and language.lower() not in ('cn', 'zh-cn'):
            return f'voice-{str(uuid.uuid4())}.{language}.mp3'
        return f'voice-{str(uuid.uuid4())}.mp3'
            
    def _fix_audio_filename(self, filename: str, language: str) -> str:
        """修复音频文件名，确保包含语言代码
        
        Args:
            filename: 原文件名
            language: 语言代码
            
        Returns:
            修正后的文件名
        """
        if f'{language}.mp3' in '.'.join(filename.split('.')[-2:]):
            return filename
        return '.'.join(filename.split('.')[:-1])+f'.{language}.mp3'

    @staticmethod
    def correct_pronunciation(text: str, language: str, correction_dict: Dict) -> str:
        """修正发音
        
        Args:
            text: 原文本
            language: 语言代码
            correction_dict: 发音修正字典
            
        Returns:
            修正后的文本
        """
        if language in correction_dict:
            for key in correction_dict[language]:
                text = text.replace(key, correction_dict[key])
        return text
    
    def synthesize_file(self, 
                       character: str,
                       text: str,
                       language: str,
                       output_path: str,
                       filename: Optional[str] = None,
                       stop_symbols: List[str] = ['|']) -> Dict:
        """合成语音文件
        
        Args:
            character: 角色名称
            text: 文本内容
            language: 语言代码
            output_path: 输出路径
            filename: 文件名
            stop_symbols: 停顿符号列表
            
        Returns:
            合成结果信息
        """
        synthesizer = Synthesizer(
            speech_key=self.subscription, 
            service_region=self.region
        )

        # 处理默认角色
        character = 'M' if character == '' else character
        
        # 设置语音配置
        synthesizer.set_voice(
            language,
            self.voice_profiles[character][language]['voiceName'],
            **self.voice_profiles[character][language]['kwargs'])
            
        # 处理文件名
        if not filename or len(filename) < 1:
            filename = self._new_audio_filename(language)
            debug_print(f"synthesize_file:", "No input file_name, generate new file name as:", filename)
        elif language.lower() not in ('cn', 'zh-cn'):
            filename = self._fix_audio_filename(filename, language)
            debug_print(f"synthesize_file:", "Filename with language code:", filename)

        # 处理文本
        debug_print(f"synthesize_file: Original:", text)
        new_text = text
        for symbol in stop_symbols:
            new_text = new_text.split(symbol)[0]
        debug_print(f"synthesize_file:", "Corrected:", new_text)

        # 合成语音
        try:
            synthesizer.synthesize(new_text, output_path, filename)
        except Exception as e:
            error_print(f"synthesize_file:", "Synthesis failed:", e)

        return {
            "file_name": filename,
            "originalText": text,
            "correctedText": new_text,
            "character": character,
        }