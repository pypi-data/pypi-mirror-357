"""工具模块，包含常量定义和辅助函数"""

from .constants import *
from .helpers import *

__all__ = [
    # Constants
    'DEFAULT_LANGUAGE',
    'LANGUAGE_ENG',
    'DEFAULT_NARRATOR',
    'VISIBLE_ACTORS',
    'INVISIBLE_ACTORS',
    'SCENARIO_ACTORS',
    'VISIBLE',
    'INVISIBLE',
    'SCENARIO',
    'LOCAL_DEFAULT_ROOT',
    'BREAK_TIME',
    'BULLET_KEY',
    'ENDING_SOUND',
    # Colors
    'RED',
    'GREEN',
    'YELLOW',
    'BLUE',
    'RESET',
    # Helper functions
    'extract_html_elements',
    'switch_to_basename',
    'cover_html_text_with_color_style',
] 
