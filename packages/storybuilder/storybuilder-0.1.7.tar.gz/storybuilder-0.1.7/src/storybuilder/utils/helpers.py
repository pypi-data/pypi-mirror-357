from bs4 import BeautifulSoup
from PIL import Image
from typing import List, Optional, TYPE_CHECKING
from ..utils.constants import (
    error_print, info_print, warn_print, debug_print, 
    RED, GREEN, YELLOW, BLUE, RESET,
    LOG_LEVEL, LOG_LEVEL_DEBUG, LOG_LEVEL_INFO, LOG_LEVEL_WARN, LOG_LEVEL_ERROR
)

import cv2
import inspect
import json
import os
import re
import uuid
import xml.etree.ElementTree as ET
if TYPE_CHECKING:
    from src.storybuilder.services.cos import CosUploader

VISIBLE_ACTORS=("boy", "girl", "cue", "eily", "eilly")
INVISIBLE_ACTORS=("", "M", "F")
SCENARIO_ACTORS=("ending", "exam", "concentrak", "notes")
DEFAULT_SCREEN_WIDTH = 960.0
DEFAULT_SCREEN_HEIGHT = 540.0

def remove_emojis(text):
    emojiPattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U0001F926-\U0001F991"
                    "]+", flags = re.UNICODE)
    return re.sub(emojiPattern, '', text)

def normalize_math_chars(text, convert_symbols=False):
    """Convert mathematical Unicode characters to their ASCII equivalents
    
    Args:
        text (str): Text containing mathematical Unicode characters
        convert_symbols (bool): Whether to convert mathematical symbols. Defaults to False.
        
    Returns:
        str: Text with mathematical characters converted to ASCII
    """
    if not isinstance(text, str):
        return text
        
    # Mathematical mapping dictionary
    math_map = {
        # Mathematical Italic Lowercase (𝑎 through 𝑧)
        '𝑎': 'a', '𝑏': 'b', '𝑐': 'c', '𝑑': 'd', '𝑒': 'e',
        '𝑓': 'f', '𝑔': 'g', '𝒉': 'h', '𝑖': 'i', '𝑗': 'j',
        '𝑘': 'k', '𝑙': 'l', '𝑚': 'm', '𝑛': 'n', '𝑜': 'o',
        '𝑝': 'p', '𝑞': 'q', '𝑟': 'r', '𝑠': 's', '𝑡': 't',
        '𝑢': 'u', '𝑣': 'v', '𝑤': 'w', '𝑥': 'x', '𝑦': 'y', '𝑧': 'z',

        # Mathematical Italic Uppercase (𝐴 through 𝑍)
        '𝐴': 'A', '𝐵': 'B', '𝐶': 'C', '𝐷': 'D', '𝐸': 'E',
        '𝐹': 'F', '𝐺': 'G', '𝐻': 'H', '𝐼': 'I', '𝐽': 'J',
        '𝐾': 'K', '𝐿': 'L', '𝑀': 'M', '𝑁': 'N', '𝑂': 'O',
        '𝑃': 'P', '𝑄': 'Q', '𝑅': 'R', '𝑆': 'S', '𝑇': 'T',
        '𝑈': 'U', '𝑉': 'V', '𝑊': 'W', '𝑋': 'X', '𝑌': 'Y', '𝑍': 'Z',
    }

    # Mathematical symbols (only included if convert_symbols=True)
    symbol_map = {
        '…': '...',  # Ellipsis
        '≤': '<=',   # Less than or equal
        '≥': '>=',   # Greater than or equal
        '×': '*',    # Multiplication
        '÷': '/',    # Division
        '≠': '!=',   # Not equal
        '≈': '~=',   # Approximately equal
        '∈': 'in',   # Element of
        '∉': 'not in', # Not element of
        '∪': 'union', # Union
        '∩': 'intersection', # Intersection
        '∅': 'empty set', # Empty set
        '∞': 'infinity', # Infinity
        '∑': 'sum',   # Summation
        '∏': 'product', # Product
        '√': 'sqrt',  # Square root
        '∫': 'integral', # Integral
        '∂': 'd',    # Partial derivative
        '∇': 'nabla', # Nabla
        'π': 'pi',   # Pi
        'θ': 'theta', # Theta
        'λ': 'lambda', # Lambda
        'μ': 'mu',    # Mu
        'σ': 'sigma', # Sigma
        'τ': 'tau',   # Tau
        'ω': 'omega', # Omega
        '±': '+/-',   # Plus-minus
        '→': '->',    # Right arrow
        '←': '<-',    # Left arrow
        '↔': '<->',   # Double arrow
    }
    
    # Always convert mathematical italics
    for math_char, ascii_char in math_map.items():
        text = text.replace(math_char, ascii_char)
    
    # Optionally convert mathematical symbols
    if convert_symbols:
        for symbol_char, ascii_char in symbol_map.items():
            text = text.replace(symbol_char, ascii_char)
    
    return text

def has_chinese_char(text):
  """Checks if a string contains at least one Chinese character.

  Args:
      text: The string to be checked.

  Returns:
      True if the string contains at least one Chinese character, False otherwise.
  """
  # Check if any character in the string falls within the Unicode range of Chinese characters
  return any(u'\u4e00' <= char <= u'\u9fff' for char in text)

def update_object(original, update, default_locale=None):
    """Updates the original object from the update object.

    Args:
        original: The object to be updated.
        update: The object containing updates.

    Returns:
        A new object with the updates applied. Ignore if update is None.
    """
    if update == None:
        return original
    
    if isinstance(update, dict):
        return {
            **(original \
                if isinstance(original, dict) \
                else ({} if original == None else {default_locale: original})), \
            **{key: update[key] for key in update}
        }
    elif isinstance(original, dict) and default_locale != None:
        original[default_locale] = update
    else:
        original = update
    return original

def get_actors(objects):
    assert isinstance(objects, list)
    actor = None
    narrator = None
    defaultObject = None
    for i, object in enumerate(objects):
        if object.get("name", None) in VISIBLE_ACTORS:
            actor = object["name"]
        elif object.get("name", None) in INVISIBLE_ACTORS:
            narrator = object["name"]
        else:
            defaultObject = object.get("name", None)
    return actor, narrator, defaultObject

def update_visible_actor(objects, actor):
    assert isinstance(objects, list) and actor in VISIBLE_ACTORS
    if len(objects) == 0:
        objects.append({"name": actor})
    else:
        for i, object in enumerate(objects):
            if object["name"] in VISIBLE_ACTORS:
                objects[i]["name"] = actor

def update_invisible_actor(objects, actor):
    assert isinstance(objects, list) and actor in INVISIBLE_ACTORS
    if len(objects) == 0:
        objects.append({"name": actor})
    else:
        for i, object in enumerate(objects):
            if object["name"] in INVISIBLE_ACTORS:
                objects[i]["name"] = actor

def switch_to_test_path(path):
    if path.startswith("/story/"):
        return "/test/" + path[len("/story/"):]
    else:
        return path

def switch_to_basename(path):
    return os.path.basename(path)

def reset_voices_to_basename(scriptList, oldNarrator, newNarrator):
    assert isinstance(scriptList, list) \
        and (oldNarrator in VISIBLE_ACTORS or oldNarrator in INVISIBLE_ACTORS) \
        and (newNarrator in VISIBLE_ACTORS or newNarrator in INVISIBLE_ACTORS)
    for i, script in enumerate(scriptList):
        if "narrator" in script and script["narrator"] == oldNarrator and "sound" in script \
            and isinstance(script["sound"], str) and len(script["sound"]) > 0:
            scriptList[i]["narrator"] = newNarrator
            scriptList[i]["sound"] = switch_to_basename(script["sound"])
            scriptList[i].pop("languages", None)

def get_image_from_board(boardObject):
    image = None
    rect = None
    caption = None
    if "content" in boardObject:
        rect = boardObject["rect"]
        image = boardObject["content"].get("image", None)
        video = boardObject["content"].get("src", None)
        videoType = boardObject["content"].get("videoType", None)
        caption = boardObject["content"].get("caption", None)
    return rect, image, video, videoType, caption

def get_html_from_board(boardObject):
    html = None
    rect = boardObject.get("rect", None)
    if "content" in boardObject:
        html = boardObject["content"].get("html", None)
    return rect, html

def get_question_from_board(boardObject):
    question = None
    options = None
    answer = None
    rect = None
    colsPerRow = 1
    fontSize = 20
    fontColor = "white"
    rect = boardObject.get("rect", rect)
    if "content" in boardObject:
        question = boardObject["content"].get("question", question)
        options = boardObject["content"].get("options", options)
        answer = boardObject["content"].get("answer", answer)
        colsPerRow = boardObject["content"].get("colsPerRow", colsPerRow)
        fontSize = boardObject["content"].get("fontSize", fontSize)
        fontColor = boardObject["content"].get("fontColor", fontColor)
    return rect, question, options, answer, colsPerRow, fontSize, fontColor

def get_subscript_from_interaction(interactionObject):
    actor = -1
    voice = -1
    figure = -1
    text = None
    duration = ""
    if "content" in interactionObject:
        text = interactionObject["content"].get("text", text)
        voice = interactionObject["content"].get("voice", voice)
        actor = interactionObject.get("actor", actor)
        figure = interactionObject.get("figure", figure)
        duration = interactionObject.get("duration", duration)
    return actor, figure, text, voice, duration

def get_bullets_from_html(html:str):
    # Define a pattern to match the content within list items (ul or li tags)
    pattern = r"<(ul|li)>(.*?)</(ul|li)>"

    # Extract content from html using findall
    matches = re.findall(pattern, html, flags=re.DOTALL)

    extracted = []
    if matches:
        # Remove tags using re.sub
        extracted = [re.sub(r"<[^>]+>", "", match[1]) for match in matches]
    return extracted

def retrieve_element_text(element):
    text_object_list = []
    if element.name:
        for child in element.children:
            text_object_list.extend(retrieve_element_text(child))
    elif element.string:
        text_object_list.append({element.parent.name: element.string.strip()})  # Add current element's text
    return text_object_list

def extract_text_from_html(html_content):
  """
  Extracts text from any <> HTML tags in the given HTML content.

  Args:
    html_content: The HTML content as a string.

  Returns:
    A string containing the extracted text.
  """

  soup = BeautifulSoup(html_content, 'html.parser')
  return soup.get_text()

def extract_html_elements(html_text:str):
    soup = BeautifulSoup(html_text, "lxml")
    
    # Extract all text into a list
    extracted_text_object_list = retrieve_element_text(soup)
    
    # Optional: Flatten the list of lists (if nested due to structure)
    if any(isinstance(item, list) for item in extracted_text_object_list):
        extracted_text_object_list = [item for sublist in extracted_text_object_list for item in sublist]

    html_template = html_text
    for string in extracted_text_object_list:
        key = next(iter(string), None)
        if key != None:
            html_template = html_template.replace(">"+string[key]+"<", ">{"+key+"}<")
    
    # Regular expression pattern to match any number of continuous <li> elements
    # Explanation of the pattern:
    # - "<li>(.*?)</li>": Matches the first <li> tag and its content (non-greedy)
    # - "(?:<li>(.*?)</li>)*": Matches zero or more repetitions of subsequent <li> tags and their content (non-greedy)
    pattern = r"<li>(.*?)</li>(?:<li>(.*?)</li>)*"
        
    # Replace each group with a single '{}'
    html_template = re.sub(pattern, "<li>{li}</li>", html_template)

    return extracted_text_object_list, html_template

def retrieve_svg_size(image_path):
    # Load the SVG file
    tree = ET.parse(image_path)
    root = tree.getroot()

    # Extract attributes from the <svg> tag
    width = root.get("width", "0")  # Get the width attribute
    if isinstance(width, str) and width.endswith("px"):
        width = width[:-2]
    height = root.get("height", "0")  # Get the height attribute
    if isinstance(height, str) and height.endswith("px"):
        height = height[:-2]
    viewBox = root.get("viewBox", "0, 0, 0, 0")  # Get the viewBox attribute

    split_pattern = r"[ ,]+"

    return [int(width), int(height)], [
        int(float(num)) for num in re.split(split_pattern, viewBox)
    ]

def retrieve_pixel_size(image_path):
    width = height = 0
    try:
        # Open the image using the Python Imaging Library (PIL)
        image = Image.open(image_path)

        # Get the width and height of the image in pixels
        width, height = image.size

        image.close()
    except OSError as e:
        error_print(f"retrieve_pixel_size: error opening image", f"{image_path}\n", e)

    # Return the width and height as a tuple
    return width, height

def retrieve_video_size(file_path):
    """获取视频文件的尺寸
    
    Args:
        file_path: 视频文件路径
        
    Returns:
        width, height: 视频的宽度和高度
    """
    try:
        video = cv2.VideoCapture(file_path)
        if not video.isOpened():
            error_print("retrieve_video_size:", "无法打开视频文件", file_path)
            return 0, 0
            
        # 获取视频的宽度和高度
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # 释放视频对象
        video.release()
        
        return width, height
    except Exception as e:
        error_print("retrieve_video_size:", f"获取视频尺寸时出错: {str(e)}")
        return 0, 0

def get_image_size(file_path):
    width = height = 0
    try:
        if ".svg" in file_path[-4:]:
            dim2, dim4 = retrieve_svg_size(file_path)
            if dim2 == [0, 0]:
                width = dim4[2]
                height = dim4[3]
            else:
                width = dim2[0]
                height = dim2[1]
        elif (
            ".jpg" in file_path[-4:]
            or ".jpeg" in file_path[-5:]
            or ".png" in file_path[-4:]
            or ".gif" in file_path[-4:]
        ):
            width, height = retrieve_pixel_size(file_path)
        elif (
            ".mp4" in file_path[-4:]
            or ".avi" in file_path[-4:]
            or ".mov" in file_path[-4:]
            or ".mkv" in file_path[-4:]
        ):
            width, height = retrieve_video_size(file_path)
    except:
        error_print("get_image_size:", "retrieve image size error for", file_path)
    return width, height

def is_valid_http_url(url_str):
    return url_str.startswith("https://") or url_str.startswith("http://")

def merge_dicts(dict1, dict2):
  """Merges two dictionaries recursively, handling different structures.

  Args:
      dict1: The first dictionary.
      dict2: The second dictionary.

  Returns:
      A new dictionary with merged key-value pairs.
  """

  merged_dict = dict1.copy()  # Start with a copy of the first dictionary
  for key, value in dict2.items():
    if key in merged_dict:
      if isinstance(merged_dict[key], dict) and isinstance(value, dict):
        # Recursively merge nested dictionaries
        merged_dict[key] = merge_dicts(merged_dict[key], value)
      else:
        # Overwrite existing key-value pair (non-nested case)
        merged_dict[key] = value
    else:
      # Add new key-value pair from the second dictionary
      merged_dict[key] = value
  return merged_dict

def fit_rect(rect: List[float], width: Optional[float] = None, height: Optional[float] = None, 
            screen_width: float = DEFAULT_SCREEN_WIDTH, screen_height: float = DEFAULT_SCREEN_HEIGHT) -> List[float]:
    """调整矩形区域以适应屏幕尺寸
    
    Args:
        rect: 矩形区域 [x, y, width, height]
        width: 图片宽度（可选）
        height: 图片高度（可选）
        screen_width: 屏幕宽度，默认 DEFAULT_SCREEN_WIDTH
        screen_height: 屏幕高度，默认 DEFAULT_SCREEN_HEIGHT
        
    Returns:
        调整后的矩形区域
        
    Note:
        - 如果提供width和height，会保持图片比例进行调整
        - 如果不提供width和height，只进行简单的屏幕适配
    """
    if width is not None and height is not None:
        # 图片比例调整
        if width / height > (rect[2] if rect[2] > 1.0 else rect[2]*screen_width) / (rect[3] if rect[3] > 1.0 else rect[3]*screen_height):
            height = round((rect[2] if rect[2] > 1.0 else rect[2]*screen_width) * height / width / (1.0 if rect[3] > 1.0 else screen_height), 3)
            width = rect[2] * 1.0
        else:
            width = round((rect[3] if rect[3] > 1.0 else rect[3]*screen_height) * width / height / (1.0 if rect[2] > 1.0 else screen_width), 3)
            height = rect[3] * 1.0

        rect[0] += round(((rect[2] if rect[2] > 1.0 else rect[2]*screen_width) \
                          - (width if width > 1.0 else width*screen_width))/screen_width/2.0, 3)
        rect[1] += round(((rect[3] if rect[3] > 1.0 else rect[3]*screen_height) \
                          - (height if height > 1.0 else height*screen_height))/screen_height/2.0, 3)
        rect[2] = width if width > 1.0 else width * screen_width
        rect[3] = height if height > 1.0 else height * screen_height
    else:
        # 简单屏幕适配
        if rect[2] > 1.0:
            rect[2] = rect[2] / screen_width
        if rect[3] > 1.0:
            rect[3] = rect[3] / screen_height
            
    return rect

def denormalize_rect(rect: List[float], screen_width: float = DEFAULT_SCREEN_WIDTH, screen_height: float = DEFAULT_SCREEN_HEIGHT) -> List[float]:
    """将标准化的矩形区域转换为像素尺寸
    
    Args:
        rect: 标准化的矩形区域 [x, y, width, height] (0.0~1.0)
        screen_width: 屏幕宽度，默认 DEFAULT_SCREEN_WIDTH
        screen_height: 屏幕高度，默认 DEFAULT_SCREEN_HEIGHT
        
    Returns:
        像素尺寸的矩形区域
        
    Note:
        - 将小于1.0的值转换为实际像素值
        - 是 normalize_rect 的反向操作
    """
    if rect[2] <= 1.0:
        rect[2] = rect[2] * screen_width
    if rect[3] <= 1.0:
        rect[3] = rect[3] * screen_height
    return rect

def normalize_rect(rect: List[float], screen_width: float = DEFAULT_SCREEN_WIDTH, screen_height: float = DEFAULT_SCREEN_HEIGHT) -> List[float]:
    """将像素尺寸的矩形区域标准化
    
    Args:
        rect: 像素尺寸的矩形区域 [x, y, width, height]
        screen_width: 屏幕宽度，默认 DEFAULT_SCREEN_WIDTH
        screen_height: 屏幕高度，默认 DEFAULT_SCREEN_HEIGHT
        
    Returns:
        标准化的矩形区域 (0.0~1.0)
        
    Note:
        - 将大于1.0的值转换为标准化值(0.0~1.0)
        - 是 denormalize_rect 的反向操作
    """
    if rect[2] > 1.0:
        rect[0] = rect[0] / screen_width
        rect[2] = rect[2] / screen_width
    if rect[3] > 1.0:
        rect[1] = rect[1] / screen_height
        rect[3] = rect[3] / screen_height
    return rect

def cover_html_text_with_color_style(html_data: str, color: str = "white") -> str:
    """用指定颜色样式覆盖未覆盖的文本，避免冗余样式。"""

    def replace_match(match):
        tag_name = match.group(1)
        attributes = match.group(2).strip()
        content = match.group(3)
        closing_tag = f"</{tag_name}>"

        style_match = re.search(r'\s+style\s*=\s*(["\'])(.*?)\1', attributes, re.IGNORECASE)
        is_already_colored = False
        if style_match:
            quote = style_match.group(1)
            existing_style = style_match.group(2)
            if "color: {color}" in existing_style.lower():
                is_already_colored = True
                updated_attributes = attributes
            else:
                updated_style = f"{existing_style}; color: {color}"
                updated_attributes = attributes.replace(style_match.group(0), f" style={quote}{updated_style}{quote}")
        else:
            updated_attributes = f"style='color: {color}'"

        opening_tag = f"<{tag_name}{' ' + updated_attributes if updated_attributes else ''}>"

        modified_content = content

        if not is_already_colored:
            # More robust approach using a loop and regex to handle nested elements
            parts = re.split(r"(<[^>]+>)", content)  # Split by tags
            modified_parts = []
            for part in parts:
                if part.startswith("<"):
                    modified_parts.append(part) # Keep tags as they are
                elif part.strip(): #check if there is non whitespace characters
                    modified_parts.append(f"<span style='color: {color};'>{part.strip()}</span>")
                else:
                    modified_parts.append(part) # keep the white spaces
            modified_content = "".join(modified_parts)

        return opening_tag + modified_content + closing_tag

    pattern = r"<(\w+)([^>]*)>((?:(?!</\1>).)*)</\1>"
    modified_html = re.sub(pattern, replace_match, html_data, flags=re.DOTALL | re.IGNORECASE)
    return modified_html

# TODO: 下面例子最外部已经有<h2 style='color: white'>，所以不需要再添加<span style='color: white'>
# <h2 style='color: white'><br/><ul><li><span style='color: white;'>14 𝑚𝑜𝑑 2 = ?</span></li><li><span style='color: white;'>9 𝑚𝑜𝑑 6 = ?</span></li><li><span style='color: white;'>17 𝑚𝑜𝑑 7 = ?</span></li><li><span style='color: white;'>13 𝑚𝑜𝑑 1 = ?</span></li><li><span style='color: white;'>1312313498324234234234233 𝑚𝑜𝑑 2 = ?</span></li></ul></h2>

def process_json_values_with_pattern(json_data, key_pattern, value_pattern, func, **func_kwargs):
    """
    扫描复杂的 JSON 对象，对键匹配 key_pattern 且值以 value_pattern 开头的条目应用函数，并仅在值发生更改时打印更改。

    Args:
        json_data: JSON 对象（字典、列表或其他有效的 JSON 结构）。
        key_pattern: 用于匹配键的正则表达式模式。
        value_pattern: 用于匹配值开头的正则表达式模式。
        func: 要应用于匹配值的函数。
        func_kwargs: 要应用于匹配值的函数的关键字参数。
    Returns:
        一个包含修改后值的新 JSON 对象，如果没有进行任何更改，则返回原始对象。
        如果 json_data 不是有效的 JSON 结构（字典或列表），则引发 TypeError。

    Examples:
        def add_prefix(image_url):
            return "https://example.com/" + image_url

        json_data = {
            "images": [{"image": "product_a.jpg"}],
            "thumbnails": [{"thumbnail": "thumb_a.jpg"}]
        }

        # 对键为 "image" 且值以 "product" 开头的条目添加前缀
        modified_json = process_json(json_data, r"^image$", r"^product", add_prefix)

        # 输出示例：
        # <image>: <product_a.jpg> -> <https://example.com/product_a.jpg>

        # 最终的 modified_json 将包含修改后的 URL。
    """

    if not isinstance(json_data, (dict, list)):
        raise TypeError("json_data must be a dict or list")

    def _process_value(key, value):
        if isinstance(value, str) and re.match(value_pattern, value):
            new_value = func(value, **func_kwargs)
            if new_value != value:
                debug_print(f"process_json_values_with_pattern: _process_value", f"<{key}>: <{value}> -> <{new_value}>")
            return new_value
        return value

    def _process_item(item):
        if isinstance(item, dict):
            new_item = {}
            for key, value in item.items():
                if re.match(key_pattern, key):
                    new_item[key] = _process_value(key, value)
                elif isinstance(value, (dict, list)):
                    new_item[key] = process_json_values_with_pattern(value, key_pattern, value_pattern, func, **func_kwargs)
                else:
                    new_item[key] = value
            return new_item
        elif isinstance(item, list):
            return [process_json_values_with_pattern(v, key_pattern, value_pattern, func, **func_kwargs) if isinstance(v, (dict, list)) else v for v in item]
        else:
            return item

    if isinstance(json_data, dict):
        return _process_item(json_data)
    elif isinstance(json_data, list):
        return _process_item(json_data)
    else:
        return json_data
    
# 基本匹配：

# 字面字符： 大部分字符按字面意义匹配自身。例如，a 匹配字符 "a"，1 匹配字符 "1"，. 匹配字符 "."。
# . (点号)： 匹配除换行符以外的任何字符。例如，a.b 匹配 "acb"、"a0b"、"a#b" 等。
# \ (反斜杠)： 转义特殊字符。如果要匹配字面意义的 .，需要使用 \.。类似地，\\ 匹配字面意义的反斜杠。
# 字符类：

# [abc]： 匹配方括号内的任何一个字符。例如，[abc] 匹配 "a"、"b" 或 "c"。
# [a-z]： 匹配从 "a" 到 "z" 的任何小写字母。
# [0-9]： 匹配从 "0" 到 "9" 的任何数字。
# [^abc]： 匹配不在方括号内的任何字符。例如，[^abc] 匹配除 "a"、"b" 或 "c" 之外的任何字符。
# \d： 匹配任何数字（等效于 [0-9]）。
# \D： 匹配任何非数字。
# \s： 匹配任何空白字符（空格、制表符、换行符）。
# \S： 匹配任何非空白字符。
# \w： 匹配任何单词字符（字母、数字和下划线）。
# \W： 匹配任何非单词字符。
# 量词：

# *：匹配前面字符或组的零次或多次出现。例如，ab*c 匹配 "ac"、"abc"、"abbc"、"abbbc" 等。
# +：匹配前面字符或组的一次或多次出现。例如，ab+c 匹配 "abc"、"abbc"、"abbbc" 等，但不匹配 "ac"。
# ?：匹配前面字符或组的零次或一次出现。例如，ab?c 匹配 "ac" 或 "abc"。
# {n}：精确匹配 n 次。例如，a{3} 匹配 "aaa"。
# {n,m}：匹配 n 到 m 次（包括 n 和 m）。例如，a{2,4} 匹配 "aa"、"aaa" 或 "aaaa"。
# 锚点：

# ^：匹配字符串的开头。在 process_json 函数的上下文中，这匹配键或值的开头。
# $：匹配字符串的结尾。
# 分组和交替：

# (abc)：将字符 "abc" 分组在一起。这对于将量词或交替应用于组很有用。
# a|b：匹配 "a" 或 "b"。
# 在 process_json 上下文中的示例：

# key_pattern = r"^image$" 且 value_pattern = r"^product"：这匹配键完全是 "image" 且值以 "product" 开头的条目。
# key_pattern = r"image" 且 value_pattern = r".*\.jpg$"：这匹配键中任何位置包含 "image" 且值以 ".jpg" 结尾的条目。
# key_pattern = r"^(image|thumbnail)$" 且 value_pattern = r"^http"：这匹配键是 "image" 或 "thumbnail" 且值以 "http" 开头的条目。
# key_pattern = r".*image.*" 且 value_pattern = r".*"：这匹配任何包含 "image" 的键和任何值。
# key_pattern = r"^product_images$" 且 value_pattern = r"^product"：这精确匹配键 "product_images" 且值以 "product" 开头。
# 重要提示：

# 原始字符串： 强烈建议对 Python 中的正则表达式模式使用原始字符串（例如，r"^image$"）。这可以防止反斜杠被解释为转义序列。
# 大小写敏感性： 默认情况下，正则表达式匹配是区分大小写的。您可以使用 re.IGNORECASE 标志（如在 process_json 函数中使用的）使其不区分大小写。
# re.match 与 re.search： process_json 函数使用 re.match，它仅在字符串的开头匹配。如果需要在字符串中的任何位置匹配模式，请使用 re.search。
import copy
from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from ..builders.story import Story
    from ..models import Scene

def update_story_scene_with_style(story: 'Story', styles_mapping: list) -> dict:
    """根据 style_dict 更新 story_object 的样式"""
    if not isinstance(styles_mapping, list):
        raise ValueError("style_dict must be dictionaries")
    
    new_story = story.copy()
    if not isinstance(new_story.pages, list) or len(new_story.pages) == 0:
        raise ValueError("story must contain a list of pages")
    
    for index, page in enumerate(new_story.pages):
        page_scene = page.scene
        if isinstance(page_scene, (dict, str)):
            for style_mapping_object in styles_mapping:
                if "from" in style_mapping_object and "to" in style_mapping_object:
                    if type(style_mapping_object["from"]) == type(page_scene):
                        if isinstance(page_scene, str) and page_scene == style_mapping_object["from"]:
                            new_story.pages[index]["scene"] = style_mapping_object["to"]
                        elif isinstance(page_scene, dict) \
                            and all(key in style_mapping_object["from"] for key in page_scene) \
                                and all(style_mapping_object["from"][key] == page_scene[key] for key in page_scene):
                            new_story.pages[index]["scene"] = style_mapping_object["to"]
    return new_story

def save_styled_story_to_file(story, story_file_path, styles_name):
    new_story = copy.deepcopy(story)
    new_story.set_styls(styles_name)
    new_story_file_path = story_file_path.replace(".json", f".{styles_name}.json")
    with open(new_story_file_path, "w") as f:
        json.dump(new_story.export(), f, ensure_ascii=False, indent=4, sort_keys=False)

    debug_print("save_styled_story_to_file:", "styles:", styles_name, "new_story_file_path:", new_story_file_path)
    return new_story_file_path

def copy_story_resource_to_story_id_path(source_path, **kwargs):
    if not kwargs.get("cos_uploader", None):
        raise ValueError("cos_uploader must be a CosUploader instance")
    
    cos_uploader = kwargs.get("cos_uploader")

    # 判断是否是包含uuid4的url
    uuid4_pattern = r".*[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}.*"
    if re.match(uuid4_pattern, source_path):
        debug_print(f"source_path is a UUID URL, skip copy {source_path}")
        return source_path

    target_path = source_path
    story_id = kwargs.get("story_id", None)
    if isinstance(story_id, str) and len(story_id) == len(str(uuid.uuid4())):
        if source_pattern:=kwargs.get("source_pattern"):
            if not source_path.startswith(source_pattern):
                debug_print(f"source_path is not correctly provided, skip copy {source_path} with source_pattern {source_pattern}")
                return source_path
            if source_pattern.endswith("/"):
                target_path = source_path.replace(source_pattern, f"{source_pattern}{story_id}/")
            else:
                target_path = source_path.replace(source_pattern, f"{source_pattern}/{story_id}")
            if kwargs.get("upload_to_cos", True):
                target_path = cos_uploader.copy2dest(source_path, target_path)
                debug_print(f"{source_path} --copied to--> {target_path}")
        else:
            debug_print(f"source_pattern is not correctly provided, skip copy {source_path}")
    else:
        debug_print(f"story_id {story_id} is not correctly provided, skip copy {source_path}")

    return target_path

def get_function_details(func):
    """Extracts details about a function for documentation.

    Args:
        func: The function object to introspect.

    Returns:
        A dictionary containing function details like name, docstring,
        and argument information.
    """
    details = {}
    details["name"] = func.__name__
    details["docstring"] = inspect.getdoc(func) or "No docstring provided."
    details["args"] = ", ".join(inspect.getargspec(func).args[1:])  # Skip self
    return details

def export_functions_for_readme(module, filename="README.md"):
    """Extracts details of all functions and interfaces in a module for README.

    Args:
        module: The Python module containing the functions.
        filename: The output filename for the README markdown (default: "README.md").

    Writes the formatted output to the specified file.
    """
    functions = [getattr(module, name) for name in dir(module) if inspect.isfunction(getattr(module, name))]
    markdown_output = "\n## Functions\n\n"
    if len(functions) > 0:
        function_details = [get_function_details(func) for func in functions]

        # Generate markdown formatted output
        for details in function_details:
            markdown_output += f"**{details['name']}**\n"
            markdown_output += f"{details['docstring']}\n"
            if details["args"]:
                markdown_output += f"Arguments: {details['args']}\n\n"

    # Write the output to the specified file
    with open(filename, "w") as f:
        f.write(markdown_output)
    info_print(f"Function details written to {filename}")