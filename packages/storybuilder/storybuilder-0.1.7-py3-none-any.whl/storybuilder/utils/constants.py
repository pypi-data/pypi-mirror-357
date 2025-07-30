"""常量定义模块"""

# 颜色常量
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
RESET  = "\033[0m"

# 语言相关常量
DEFAULT_LANGUAGE = "zh-CN"
LANGUAGE_ENG = "en-US"

# 角色相关常量
DEFAULT_NARRATOR = "M"
VISIBLE_ACTORS = ("boy", "girl", "cue", "eily", "eilly", "sports-boy")
MULTIPLE_POSTURE_ACTORS = ("boy", "girl", "sports-boy")
VISIBLE = 0
INVISIBLE_ACTORS = ("", "M", "F")
INVISIBLE = 1
SCENARIO_ACTOR_ENDING = "ending"
SCENARIO_ACTOR_EXAM = "exam"
SCENARIO_ACTOR_CONCENTRAK = "concentrak"
SCENARIO_ACTOR_NOTES = "notes"
SCENARIO_ACTORS = (SCENARIO_ACTOR_ENDING, SCENARIO_ACTOR_EXAM, 
                   SCENARIO_ACTOR_CONCENTRAK, SCENARIO_ACTOR_NOTES)
SCENARIO = 2

# 场景类型定义
SCENE_CLASSROOM = "classroom"
SCENE_BLACKBOARD = "blackboard"
SCENE_EXAM = "exam"
SCENE_NOTES = "notes"
SCENE_COVER = "cover"
SCENE_CONCENTRAK = "concentrak"
    

# 路径常量
LOCAL_DEFAULT_ROOT = "./test"
PRODUCTION_ROOT="/story/"
TEST_ROOT="/test/"

# 其他常量
BREAK_TIME = "<break time=\"1500ms\"/>"
BULLET_KEY = "li"
ENDING_SOUND = "/story/audios/OurMusicBox - 24 Hour Coverage - intro.mp3"

# Debug mode
DEBUG_MODE = False

# 日志级别
LOG_LEVEL = 0
LOG_LEVEL_DEBUG = 4
LOG_LEVEL_INFO = 3
LOG_LEVEL_WARN = 2
LOG_LEVEL_ERROR = 1

# 设置日志级别
def set_log_level(level: int = LOG_LEVEL_DEBUG):
    """设置日志级别
    
    0: 不打印日志
    1: 打印错误日志
    2: 打印警告日志
    3: 打印信息日志
    4: 打印调试日志
    """
    global LOG_LEVEL
    LOG_LEVEL = level

def get_log_level():
    """获取日志级别"""
    return LOG_LEVEL

def _print_log(level: int, *args, **kwargs):
    """打印日志"""
    if LOG_LEVEL >= level:
        print(*args, **kwargs)

def debug_print(*args, **kwargs):
    """调试打印函数"""
    _print_log(4, "DEBUG:", *args, **kwargs)

def info_print(*args, **kwargs):
    """信息打印函数"""
    _print_log(3, BLUE, "INFO:", *args, RESET, **kwargs)

def warn_print(*args, **kwargs):
    """警告打印函数"""
    _print_log(2, YELLOW, "WARNING:", *args, RESET, **kwargs)

def error_print(*args, **kwargs):
    """错误打印函数"""
    _print_log(1, RED, "ERROR:", *args, RESET, **kwargs)

# 导出所有常量
__all__ = [
    'RED', 'GREEN', 'YELLOW', 'BLUE', 'RESET',
    'DEFAULT_LANGUAGE', 'LANGUAGE_ENG',
    'DEFAULT_NARRATOR',
    'VISIBLE_ACTORS', 'INVISIBLE_ACTORS', 'SCENARIO_ACTORS',
    'VISIBLE', 'INVISIBLE', 'SCENARIO',
    'LOCAL_DEFAULT_ROOT',
    'BREAK_TIME', 'BULLET_KEY', 'ENDING_SOUND',
    'SCENE_CLASSROOM', 'SCENE_BLACKBOARD', 'SCENE_EXAM', 'SCENE_NOTES', 'SCENE_COVER', 'SCENE_CONCENTRAK'
] 