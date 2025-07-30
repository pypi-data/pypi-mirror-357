"""外部服务模块"""

from .cos import CosUploader
from .voice import VoiceSynthesizer
from .speech import Synthesizer

__all__ = [
    'CosUploader',
    'VoiceSynthesizer',
    'Synthesizer'
] 