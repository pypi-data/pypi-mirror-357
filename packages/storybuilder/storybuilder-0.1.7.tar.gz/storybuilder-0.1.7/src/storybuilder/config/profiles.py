from typing import Dict, Any, Final, List

# 角色语音配置
CHARACTER_VOICE_PROFILES: Final[Dict[str, Dict[str, Dict[str, Any]]]] = {
    '': {
        'zh-CN': {
            'voiceName': 'zh-CN-YunxiNeural',
            'kwargs': {}
        },
        'en-US': {
            'voiceName': 'en-US-AndrewMultilingualNeural',
            'kwargs': {}
        }
    },
    'cue': {
        'zh-CN': {
            'voiceName': 'zh-CN-XiaoxiaoNeural',
            'kwargs': {
                'style': 'affectionate',
            }
        },
        'en-US': {
            'voiceName': 'en-US-AriaNeural',
            'kwargs': {
                'style': 'cheerful',
            }
        }
    },
    'eily': {  # 别名，使用与 cue 相同的配置
        'zh-CN': {
            'voiceName': 'zh-CN-XiaoxiaoNeural',
            'kwargs': {
                'style': 'affectionate',
            }
        },
        'en-US': {
            'voiceName': 'en-US-AriaNeural',
            'kwargs': {
                'style': 'cheerful',
            }
        }
    },
    'boy': {
        'zh-CN': {
            'voiceName': 'zh-CN-YunxiNeural',
            'kwargs': {
                'role': 'Boy',
                'style': 'Default',
                'prosody': {
                    'rate': '+4.00%'
                }
            }
        },
        'en-US': {
            'voiceName': 'zh-CN-YunxiNeural',
            'kwargs': {
                'role': 'Boy',
                'style': 'chat'
            }
        }
    },
    'girl': {
        'zh-CN': {
            'voiceName': 'zh-CN-XiaoshuangNeural',
            'kwargs': {
                'prosody': {
                    'rate': '+8.00%'
                }
            }
        },
        'en-US': {
            'voiceName': 'en-US-AnaNeural',
            'kwargs': {
                'style': 'chat'
            }
        }
    },
    'sports-boy': {
        'zh-CN': {
            'voiceName': 'zh-CN-YunjieNeural',
            'kwargs': {
                'prosody': {
                    'rate': '+4.00%'
                }
            }
        },
        'en-US': {
            'voiceName': 'en-US-BrandonNeural',
            'kwargs': {}
        }
    },
    'M': {  # 默认男性角色
        'zh-CN': {
            'voiceName': 'zh-CN-YunxiNeural',
            'kwargs': {}
        },
        'en-US': {
            'voiceName': 'en-US-AndrewMultilingualNeural',
            'kwargs': {
                'style': 'e-learning'
            }
        }
    },
    'F': {  # 默认女性角色
        'zh-CN': {
            'voiceName': 'zh-CN-XiaohanNeural',
            'kwargs': {}
        },
        'en-US': {
            'voiceName': 'en-US-JennyNeural',
            'kwargs': {
                'style': 'newscast'
            }
        }
    }
}

# 发音修正字典
PRONUNCIATION_DICTIONARY: Final[Dict[str, Dict[str, str]]] = {
    "zh-CN": {
        '羞臊': '羞sào',
        '数数': '暑shù',
        '∠': '角',
        '°': '度',
        '<ul>': '',
        '</ul>': '',
        '<li>': '',
        '</li>': '。',
        '·': '-',
        '>': '大于',
        '<': '小于',
        '>=': '大于等于',
        '<=': '小于等于',
        'WHO': 'W-H-O',
        'elif': 'L-If',
        'for': 'four',
        '\n': '',
        '_': '',
        '≡': '同余于'
    },
    "en-US": {
        '<ul>': '',
        '</ul>': '',
        '<li>': '',
        '</li>': '.',
        '\n': '',
        '_': '',
        '≡': ' is congruent to '
    }
}

# 场景样式配置
STORY_SCENARIO_STYLES: Final[Dict[str, Dict[str, Any]]] = {
    "shinkai_makoto": {  # 新海诚风格
        "scenarios": {
            "cover": {"bgColor": "#C1D0BA"},
            "classroom": "475dc094-e147-478e-a1cf-770df5efa081",
            "notes": {
                "scene": "ce3ae229-7e6b-4e10-9d0a-e5e53d923d61",
                "htmlTemplate": "<h3 style='color:white'><ul><li></li></ul></h3>",
                "rect": [0.2, 0.25, 0.6, 0.45]
            },
            "exam": {
                "scene": "a65ed1dc-9e27-4c3d-a5f7-090fc2af4917",
                "rect": [0.2, 0.25, 0.6, 0.45],
                "transform": "scale(1.5)",
                "fontColor": "white",
                "fontSize": "20px",
                "colsPerRow": 2
            },
            "blackboard": {"bgColor": "#98A698"},
            "concentrak": {
                "index": "0bd6c33e-31eb-4083-8dd8-ee07837bc975",
                "bgColor": "#C1D0BA"
            },
        },
        "frame": "10px solid #843C0C",
        "positions": {
            "left": [0.2, 0.05],
            "right": [0.8, 0.05],
            "right-bottom": [0.85, -0.05],
        },
        "popup": 11,
        "transform": None
    },
    "close_up": {  # 特写风格
        "scenarios": {
            "cover": "5cdab8ba-c028-45ea-87cc-b0d75dd81e10",
            "classroom": "b99b0dc2-0387-4a4f-9c61-308b362cb8f6",
            "notes": {
                "scene": "6c5c45c3-070f-439a-a6f7-a366a04c357c",
                "htmlTemplate": "<p><ul style='color: white' size='5'><li></li></ul></p>",
                "rect": [0.15, 0.25, 0.65, 0.45]
            },
            "exam": {
                "scene": "ea874992-c7a9-44c4-8bef-13cad8cee917",
                "rect": [0.15, 0.25, 0.65, 0.45],
                "transform": "scale(1.5)",
                "fontColor": "white",
                "fontSize": "20px",
                "colsPerRow": 2
            },
            "blackboard": "e183c517-cbb7-4831-bcf6-efd310ee8790",
            "concentrak": {
                "index": "0bd6c33e-31eb-4083-8dd8-ee07837bc975",
                "bgColor": "#9BB9BF"
            },
        },
        "frame": "10px solid #843C0C",
        "positions": {
            "left": [0.2, -0.25],
            "right": [0.8, -0.25],
            "right-bottom": [0.85, -0.05],
        },
        "popup": 10,
        "transform": "scale(2)"
    }
}

#角色位置配置
CHARACTER_POSITIONS = {
    "boy": {
        "half": "right-bottom",
        "standright": "right",
        "-stand-": "left"
    },
    "sports-boy": {
        "half": "right-bottom", 
        "standright": "right",
        "-stand-": "left"
    },
    "girl": {
        "half": "right-bottom",
        "-stand-": "right"
    }
}

# 导出所有常量
__all__ = [
    'CHARACTER_VOICE_PROFILES',
    'PRONUNCIATION_DICTIONARY',
    'STORY_SCENARIO_STYLES',
    'CHARACTER_POSITIONS'
]