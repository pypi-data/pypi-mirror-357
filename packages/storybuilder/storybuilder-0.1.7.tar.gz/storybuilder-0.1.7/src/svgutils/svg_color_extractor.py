import re
from xml.etree import ElementTree as ET
from collections import defaultdict
import sys

def extract_colors_from_svg(svg_path):
    """提取 SVG 文件中使用的所有颜色"""
    # 读取 SVG 文件
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
    except Exception as e:
        print(f"读取 SVG 文件时出错: {str(e)}")
        return None

    colors = defaultdict(int)
    
    # 颜色属性列表
    color_attributes = [
        'fill', 'stroke', 'color', 'stop-color', 
        'flood-color', 'lighting-color'
    ]
    
    # 颜色格式的正则表达式
    color_patterns = {
        'hex': r'#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})',
        'rgb': r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)',
        'rgba': r'rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([0-9.]+)\s*\)',
        'hsl': r'hsl\(\s*(\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%\s*\)',
        'named': r'(aliceblue|antiquewhite|aqua|aquamarine|azure|beige|bisque|black|blanchedalmond|blue|blueviolet|brown|burlywood|cadetblue|chartreuse|chocolate|coral|cornflowerblue|cornsilk|crimson|cyan|darkblue|darkcyan|darkgoldenrod|darkgray|darkgreen|darkgrey|darkkhaki|darkmagenta|darkolivegreen|darkorange|darkorchid|darkred|darksalmon|darkseagreen|darkslateblue|darkslategray|darkslategrey|darkturquoise|darkviolet|deeppink|deepskyblue|dimgray|dimgrey|dodgerblue|firebrick|floralwhite|forestgreen|fuchsia|gainsboro|ghostwhite|gold|goldenrod|gray|green|greenyellow|grey|honeydew|hotpink|indianred|indigo|ivory|khaki|lavender|lavenderblush|lawngreen|lemonchiffon|lightblue|lightcoral|lightcyan|lightgoldenrodyellow|lightgray|lightgreen|lightgrey|lightpink|lightsalmon|lightseagreen|lightskyblue|lightslategray|lightslategrey|lightsteelblue|lightyellow|lime|limegreen|linen|magenta|maroon|mediumaquamarine|mediumblue|mediumorchid|mediumpurple|mediumseagreen|mediumslateblue|mediumspringgreen|mediumturquoise|mediumvioletred|midnightblue|mintcream|mistyrose|moccasin|navajowhite|navy|oldlace|olive|olivedrab|orange|orangered|orchid|palegoldenrod|palegreen|paleturquoise|palevioletred|papayawhip|peachpuff|peru|pink|plum|powderblue|purple|red|rosybrown|royalblue|saddlebrown|salmon|sandybrown|seagreen|seashell|sienna|silver|skyblue|slateblue|slategray|slategrey|snow|springgreen|steelblue|tan|teal|thistle|tomato|turquoise|violet|wheat|white|whitesmoke|yellow|yellowgreen)'
    }

    def find_colors_in_style(style_text):
        """在 style 属性中查找颜色"""
        if not style_text:
            return
            
        for attr in color_attributes:
            pattern = f"{attr}:\s*([^;]+)"
            matches = re.finditer(pattern, style_text)
            for match in matches:
                color_value = match.group(1).strip()
                colors[color_value] += 1

    def process_element(element):
        """处理 SVG 元素"""
        # 检查 style 属性
        style = element.get('style')
        if style:
            find_colors_in_style(style)
        
        # 检查颜色属性
        for attr in color_attributes:
            color = element.get(attr)
            if color:
                colors[color] += 1
        
        # 递归处理子元素
        for child in element:
            process_element(child)

    # 处理整个 SVG
    process_element(root)
    
    # 整理颜色结果
    result = {
        'hex': [],
        'rgb': [],
        'rgba': [],
        'hsl': [],
        'named': [],
        'other': []
    }
    
    for color in colors.keys():
        color = color.lower().strip()
        matched = False
        
        for color_type, pattern in color_patterns.items():
            if re.match(pattern, color):
                result[color_type].append(color)
                matched = True
                break
        
        if not matched:
            result['other'].append(color)
    
    return result

def print_colors(colors):
    """打印颜色结果"""
    if not colors:
        print("未找到颜色")
        return
        
    print("\n=== SVG 文件中使用的颜色 ===")
    for color_type, color_list in colors.items():
        if color_list:
            print(f"\n{color_type.upper()} 颜色:")
            for color in sorted(color_list):
                print(f"  - {color}")

# 测试代码
if __name__ == "__main__":
    if len(sys.argv) > 1:
        svg_path = sys.argv[1]
    else:
        print("请提供 SVG 文件路径作为参数")
        print("用法: python svg_color_extractor.py <svg文件路径>")
        sys.exit(1)
        
    try:
        colors = extract_colors_from_svg(svg_path)
        print_colors(colors)
    except Exception as e:
        print(f"处理 SVG 文件时出错: {str(e)}")