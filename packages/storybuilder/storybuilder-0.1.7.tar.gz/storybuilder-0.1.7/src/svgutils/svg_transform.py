import xml.etree.ElementTree as ET
import re
import sys
import os
import argparse
import glob
import math

def extract_translate_values(transform_str):
    """
    只提取 translate 变换值，忽略其他变换
    
    Args:
        transform_str (str): Transform 属性字符串
        
    Returns:
        tuple: (tx, ty) 平移值 或 None
    """
    if not transform_str:
        return None
    
    # 只匹配 translate(x y) 或 translate(x,y)
    translate_pattern = r'translate\(([-\d.]+)(?:,|\s+)([-\d.]+)\)'
    translate_match = re.search(translate_pattern, transform_str)
    
    if translate_match:
        return float(translate_match.group(1)), float(translate_match.group(2))
    
    return None

def extract_matrix_values(transform_str):
    """
    从 SVG transform 属性字符串中提取矩阵值。
    假定矩阵格式为 "matrix(a, b, c, d, e, f)"。

    Args:
        transform_str (str): transform 属性字符串。

    Returns:
        list: 包含六个矩阵值 (a, b, c, d, e, f) 的列表，类型为浮点数。
               如果未找到矩阵变换，则返回 None。
    """

    if not transform_str:
        return None

    matrix_pattern = r'matrix\(([-\d.]+)(?:,\s+)([-\d.]+)(?:,\s+)([-\d.]+)(?:,\s+)([-\d.]+)(?:,\s+)([-\d.]+)(?:,\s+)([-\d.]+)\)'
    matrix_match = re.search(matrix_pattern, transform_str)

    if matrix_match:
        return [float(group) for group in matrix_match.groups()]
    else:
        return None

def extract_scale_values(transform_str):
    """
    从 SVG transform 属性字符串中提取缩放值 (sx, sy)。
    同时处理 "scale(s)" (统一缩放) 和 "scale(sx, sy)" (非统一缩放)。

    Args:
        transform_str (str): transform 属性字符串。

    Returns:
        tuple: 包含缩放值 (sx, sy) 的元组，类型为浮点数。
               如果未找到缩放变换，则返回 None。
    """

    if not transform_str:
        return None

    # 改进的模式，同时处理统一和非统一缩放
    scale_pattern = r'scale\(([-\d.]+)(?:,\s+)([-\d.]+)\)?'
    scale_match = re.search(scale_pattern, transform_str)

    if scale_match:
        groups = scale_match.groups()
        if len(groups) == 1:  # 统一缩放
            return float(groups[0]), float(groups[0])
        else:  # 非统一缩放
            return float(groups[0]), float(groups[1])
    else:
        return None

def find_g_element(root):
    """
    Find g element with or without namespace.
    
    Args:
        root: Root element of the SVG
        
    Returns:
        element: First g element found or None
    """
    # Try with SVG namespace
    g_element = root.find('.//{http://www.w3.org/2000/svg}g')
    if g_element is not None:
        return g_element
        
    # Try without namespace
    g_element = root.find('.//g')
    return g_element

def remove_namespace_prefix(root):
    """
    Remove namespace prefixes from all elements and attributes.
    
    Args:
        root: Root element of the XML tree
    """
    # Remove namespace prefix from element tags
    for elem in root.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1]
    
    # Store the original SVG namespace
    svg_ns = {'xmlns': 'http://www.w3.org/2000/svg'}
    
    # Clear other namespaces but keep the SVG namespace
    if root.tag.lower() == 'svg':
        # Remove all namespaces
        for key in list(root.attrib.keys()):
            if key.startswith('xmlns:'):
                del root.attrib[key]
        # Ensure SVG namespace is present
        root.attrib.update(svg_ns)

def format_number(num):
    """
    格式化数字，保留两位小数并移除尾随的零
    
    Args:
        num (float): 要格式化的数字
        
    Returns:
        str: 格式化后的数字字符串
    """
    # 先格式化为两位小数
    formatted = f"{num:.2f}"
    # 如果有小数点
    if '.' in formatted:
        # 移除尾随的零
        formatted = formatted.rstrip('0')
        # 如果只剩小数点，移除它
        formatted = formatted.rstrip('.')
    return formatted

def format_path_data(path_data):
    """
    格式化路径数据，移除命令字母周围的空格
    
    Args:
        path_data (str): 原始路径数据
        
    Returns:
        str: 格式化后的路径数据
    """
    # 将命令字母和数字分开
    parts = []
    current_number = ''
    
    for char in path_data:
        if char.isalpha():
            if current_number:
                parts.append(current_number.strip())
                current_number = ''
            parts.append(char)
        elif char.isspace() or char == ',':
            if current_number:
                parts.append(current_number.strip())
                current_number = ''
        else:
            current_number += char
    
    if current_number:
        parts.append(current_number.strip())
    
    # 重新组合路径数据，移除命令字母周围的空格
    formatted = ''
    i = 0
    while i < len(parts):
        if parts[i] in 'MmLlCcZzHhVvSsQqTtAa':
            # 添加命令字母，不加空格
            formatted += parts[i]
            i += 1
            # 添加该命令的参数，用空格分隔
            while i < len(parts) and not parts[i].isalpha():
                formatted += parts[i]
                if i + 1 < len(parts) and not parts[i + 1].isalpha():
                    formatted += ' '
                i += 1
        else:
            formatted += parts[i]
            if i + 1 < len(parts):
                formatted += ' '
            i += 1
    
    return formatted

def process_element(element, tx, ty):
    """处理单个元素的变换（已修改直接应用坐标变换）"""
    if element.tag.endswith('path') or element.tag == 'path':
        d_attr = element.get('d')
        if not d_attr:
            return
            
        # 移除元素的transform属性（如果存在）
        if 'transform' in element.attrib:
            element.attrib.pop('transform')
        
        # 直接应用坐标变换到路径数据
        new_d = apply_translate_to_path(d_attr, tx, ty)
        element.set('d', new_d)

def apply_translate_to_path(d, tx, ty):
    """将平移直接应用到路径数据（增强版）"""
    commands = re.findall(r'([A-Za-z])([^A-Za-z]*)', d)
    new_d = []
    
    current_pos = [0, 0]  # 当前绝对坐标
    initial_pos = None    # 路径起始点
    
    for cmd, params in commands:
        is_relative = cmd.islower()
        base_cmd = cmd.upper()
        params = [float(p) for p in re.findall(r'[-+]?\d*\.?\d+', params)]
        
        translated = []
        i = 0
        
        while i < len(params):
            if base_cmd in ('M', 'L', 'C', 'S', 'Q', 'T', 'A'):
                # 处理坐标对
                x = params[i] + (0 if is_relative else tx)
                y = params[i+1] + (0 if is_relative else ty)
                
                # 更新当前绝对坐标
                if is_relative:
                    current_pos[0] += params[i]
                    current_pos[1] += params[i+1]
                else:
                    current_pos[0] = x
                    current_pos[1] = y
                
                # 记录初始位置（针对M命令）
                if base_cmd == 'M' and initial_pos is None:
                    initial_pos = current_pos.copy()
                
                translated.extend([x, y])
                i += 2
                
            elif base_cmd in ('H', 'h'):
                # 水平线处理
                x = params[i] + (0 if is_relative else tx)
                translated.append(x)
                
                # 更新当前X坐标
                if is_relative:
                    current_pos[0] += params[i]
                else:
                    current_pos[0] = x
                i += 1
                
            elif base_cmd in ('V', 'v'):
                # 垂直线处理
                y = params[i] + (0 if is_relative else ty)
                translated.append(y)
                
                # 更新当前Y坐标
                if is_relative:
                    current_pos[1] += params[i]
                else:
                    current_pos[1] = y
                i += 1
                
            elif base_cmd == 'Z':
                # 闭合路径时重置坐标
                if initial_pos:
                    current_pos = initial_pos.copy()
                break  # Z命令无参数
                
            else:
                # 未知命令保留原始参数
                translated.append(params[i])
                i += 1
        
        # 生成新命令
        if base_cmd == 'Z':
            new_d.append('Z')
        elif translated:
            new_cmd = cmd if is_relative else base_cmd
            formatted = ' '.join(map(format_number, translated))
            new_d.append(f"{new_cmd}{formatted}")
    
    return ' '.join(new_d).replace(' -', '-')

def remove_duplicate_paths(root):
    """
    移除重复的路径元素，保留最上层的路径
    
    Args:
        root: SVG的根元素
    """
    # 收集所有路径及其数据
    all_paths = []  # 所有路径的列表，保持顺序
    path_data = {}  # key: 路径元素, value: 标准化的路径数据
    
    # 遍历所有路径元素
    for path in root.findall('.//path') + root.findall('.//{http://www.w3.org/2000/svg}path'):
        d = path.get('d')
        if d:
            # 标准化路径数据（移除多余空格和格式化数字）
            if isinstance(d, dict):
                normalized_d = format_path_data(' '.join(d['d'].split()))
            else:
                normalized_d = format_path_data(' '.join(d.split()))
            all_paths.append(path)
            path_data[path] = normalized_d
    
    print(f"Initial path count: {len(all_paths)}")
    
    # 找出要保留的路径（每个相同数据只保留最后一个）
    paths_to_keep = {}  # key: 标准化的路径数据, value: 要保留的路径元素
    for path in reversed(all_paths):  # 从后向前遍历，这样自动保留最后出现的路径
        normalized_d = path_data[path]
        if normalized_d not in paths_to_keep:
            paths_to_keep[normalized_d] = path
    
    # 移除不需要保留的路径
    removed_count = 0
    for path in all_paths:
        normalized_d = path_data[path]
        if paths_to_keep[normalized_d] != path:  # 如果不是要保留的那个路径
            # 找到父元素
            for parent in root.iter():
                if path in list(parent):
                    try:
                        parent.remove(path)
                        removed_count += 1
                        print(f"Removed duplicate path: {normalized_d[:50]}...")
                        break
                    except:
                        print(f"Warning: Failed to remove path")
    
    if removed_count > 0:
        print(f"Total removed duplicate paths: {removed_count}")

def process_g_elements(root):
    """处理SVG中的g元素"""
    # 查找所有g元素
    for g in root.findall('.//g'):
        transform = g.get('transform', '')
        
        # 提取translate值
        translation = extract_translate_values(transform)
        if translation:
            tx, ty = translation
            
            # 递归处理子元素，应用平移
            def apply_translation(element, offset_x, offset_y):
                if element.tag.endswith('path') or element.tag == 'path':
                    # 处理路径坐标
                    process_element(element, offset_x, offset_y)
                # 继续处理子元素
                for child in element:
                    apply_translation(child, offset_x, offset_y)
            
            # 应用平移并移除g元素的transform
            apply_translation(g, tx, ty)
            g.attrib.pop('transform')

        # 处理scale变换（保持原有逻辑）
        scale_match = re.search(r'scale\(([-\d.]+)(?:[,\s]+([-\d.]+))?\)', transform)
        if scale_match:
            sx = float(scale_match.group(1))
            sy = float(scale_match.group(2)) if scale_match.group(2) else sx
            
            # 更新子元素
            for child in g:
                # 这里需要添加将scale应用到路径坐标的逻辑
                process_scale(child, sx, sy)
            
            g.attrib.pop('transform')

def process_scale(element, sx, sy):
    """处理scale变换"""
    if element.tag.endswith('path') or element.tag == 'path':
        d_attr = element.get('d')
        if not d_attr:
            return
            
        # 移除元素的transform属性（如果存在）
        if 'transform' in element.attrib:
            element.attrib.pop('transform')
        
        # 直接应用缩放到路径数据
        new_d = apply_scale_to_path(d_attr, sx, sy)
        element.set('d', new_d)

def apply_scale_to_path(d, sx, sy):
    """将缩放直接应用到路径数据"""
    commands = re.findall(r'([A-Za-z])([^A-Za-z]*)', d)
    new_d = []
    
    for cmd, params in commands:
        # 处理相对/绝对坐标
        is_relative = cmd.islower()
        cmd = cmd.upper()
        params = [float(p) for p in re.findall(r'[-+]?\d*\.?\d+', params)]
        
        # 应用缩放变换
        scaled_params = []
        i = 0
        while i < len(params):
            if cmd in ('M', 'L', 'C', 'S', 'Q', 'T', 'A'):
                x = params[i] * (sx if not is_relative else 1)
                y = params[i+1] * (sy if not is_relative else 1)
                scaled_params.extend([x, y])
                i += 2
            elif cmd in ('H', 'h'):
                x = params[i] * (sx if not is_relative else 1)
                scaled_params.append(x)
                i += 1
            elif cmd in ('V', 'v'):
                y = params[i] * (sy if not is_relative else 1)
                scaled_params.append(y)
                i += 1
            else:  # Z命令不需要处理
                pass
                
        # 重新生成命令字符串
        new_cmd = cmd.lower() if is_relative else cmd
        new_d.append(f"{new_cmd}{' '.join(map(format_number, scaled_params))}")
    
    return ' '.join(new_d).replace(' -', '-').strip()

def apply_translate_from_g(svg_path, output_path):
    """
    Extracts translate transform from all <g> elements and applies them to child elements.
    Handles SVG files with or without namespace.
    
    Args:
        svg_path (str): Path to input SVG file
        output_path (str): Path where modified SVG will be saved
    """
    # Parse the SVG file
    tree = ET.parse(svg_path)
    root = tree.getroot()
    
    # 记录原始内容
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    original_content = ET.tostring(root, encoding='unicode')
    
    # 处理所有g元素的变换
    process_g_elements(root)
    
    # Remove namespace prefixes
    remove_namespace_prefix(root)
    
    # 在写入文件前添加最终路径计数
    final_path_count = len(root.findall('.//path')) + len(root.findall('.//{http://www.w3.org/2000/svg}path'))
    print(f"Final path count: {final_path_count}")
    
    # 获取处理后的内容
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    processed_content = ET.tostring(root, encoding='unicode')
    
    # 只有当内容真正发生变化时才写入文件
    if processed_content != original_content:
        # Custom write function to output clean XML
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(processed_content)
        print(f"File modified: {output_path}")
    else:
        print(f"No changes needed for: {output_path}")

def process_folder(input_folder, output_folder=None, recursive=True):
    """
    Process all SVG files in a folder.
    
    Args:
        input_folder (str): Input folder path
        output_folder (str, optional): Output folder path. If not provided, will overwrite input files
        recursive (bool): Whether to process subfolders recursively
    
    Returns:
        dict: Processing statistics
    """
    stats = {
        'total_files': 0,
        'successful': 0,
        'failed': 0,
        'failed_files': []
    }
    
    # 指定了输文夹，确它存在
    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
    
    def process_file(file_path):
        if not file_path.lower().endswith('.svg'):
            return
            
        stats['total_files'] += 1
        
        # 确定输出路径
        if output_folder:
            rel_path = os.path.relpath(file_path, input_folder)
            out_path = os.path.join(output_folder, rel_path)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
        else:
            out_path = file_path
        
        try:
            apply_translate_from_g(file_path, out_path)
            stats['successful'] += 1
            print(f"Successfully processed: {file_path}")
        except Exception as e:
            stats['failed'] += 1
            stats['failed_files'].append(file_path)
            print(f"Failed to process {file_path}: {str(e)}")
    
    # 遍历文件夹
    if recursive:
        for root, _, files in os.walk(input_folder):
            for file in files:
                process_file(os.path.join(root, file))
    else:
        for file in os.listdir(input_folder):
            process_file(os.path.join(input_folder, file))
    
    return stats

def process_folder_with_action(input_folder, output_folder, recursive, action_func):
    """
    通用的文件夹处理函数
    
    Args:
        input_folder (str): 输入文件夹路径
        output_folder (str): 输出文件夹路径
        recursive (bool): 是否递归处理子文件夹
        action_func (callable): 处理单个文件的函数
    """
    stats = {
        'total_files': 0,
        'successful': 0,
        'failed': 0,
        'failed_files': []
    }
    
    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
    
    def process_file(file_path):
        if not file_path.lower().endswith('.svg'):
            return
            
        stats['total_files'] += 1
        
        if output_folder:
            rel_path = os.path.relpath(file_path, input_folder)
            out_path = os.path.join(output_folder, rel_path)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
        else:
            out_path = file_path
        
        try:
            action_func(file_path, out_path)
            stats['successful'] += 1
            print(f"Successfully processed: {file_path}")
        except Exception as e:
            stats['failed'] += 1
            stats['failed_files'].append(file_path)
            print(f"Failed to process {file_path}: {str(e)}")
    
    if recursive:
        for root, _, files in os.walk(input_folder):
            for file in files:
                process_file(os.path.join(root, file))
    else:
        for file in os.listdir(input_folder):
            process_file(os.path.join(input_folder, file))
    
    return stats

def print_stats(stats):
    """打印处理统计信息"""
    print("\nProcessing Summary:")
    print(f"Total files: {stats['total_files']}")
    print(f"Successful: {stats['successful']}")
    print(f"Failed: {stats['failed']}")
    
    if stats['failed'] > 0:
        print("\nFailed files:")
        for file in stats['failed_files']:
            print(f"- {file}")

def circle_to_path(cx, cy, r):
    """
    将圆形转换为SVG路径命令
    
    Args:
        cx (float): 圆心x坐标
        cy (float): 圆心y坐标
        r (float): 半径
        
    Returns:
        str: SVG路径数据
    """
    # 使用四个贝塞尔曲线来近似一个圆
    # 魔术数字 0.552284749831 是为了使贝塞尔曲线最大程度接近圆形
    c = 0.552284749831
    cr = r * c
    
    return (
        f"M{cx-r},{cy} "  # 起点：左中
        f"C{cx-r},{cy-cr} {cx-cr},{cy-r} {cx},{cy-r} "  # 第一段：到上中
        f"C{cx+cr},{cy-r} {cx+r},{cy-cr} {cx+r},{cy} "  # 第二：到右中
        f"C{cx+r},{cy+cr} {cx+cr},{cy+r} {cx},{cy+r} "  # 第三段：到下中
        f"C{cx-cr},{cy+r} {cx-r},{cy+cr} {cx-r},{cy} "  # 第四段：回到起点
        f"Z"  # 闭合路径
    )

def convert_circle_to_path(element):
    """
    将circle元素转换为等效的path元素
    
    Args:
        element: circle元素
        
    Returns:
        element: 新的path元素
    """
    # 获取circle的属性
    cx = float(element.get('cx', '0').rstrip('px'))
    cy = float(element.get('cy', '0').rstrip('px'))
    r = float(element.get('r', '0').rstrip('px'))
    
    # 创建新的path元素
    path = ET.Element('path')
    
    # 复制所有属性
    for key, value in element.attrib.items():
        if key not in ['cx', 'cy', 'r']:
            path.set(key, value)
    
    # 设置路径数据
    path.set('d', circle_to_path(cx, cy, r))
    
    return path

def convert_circles(root):
    """
    换SVG中的所有circle元素为path元素
    
    Args:
        root: SVG的根元素
    """
    # 计数转换的圆形数量
    converted_count = 0
    
    # 查找所有circle元素（包含命名空间的和不包含的）
    circles = root.findall('.//circle') + root.findall('.//{http://www.w3.org/2000/svg}circle')
    
    if circles:
        print(f"Found {len(circles)} circle elements")
    
    for circle in circles:
        # 创建新的path元素
        path = convert_circle_to_path(circle)
        
        # 找到circle的父元素
        for parent in root.iter():
            if circle in list(parent):
                # 在相同位置插入新的path元素
                index = list(parent).index(circle)
                parent.insert(index, path)
                # 移除原始的circle元素
                parent.remove(circle)
                converted_count += 1
                break
    
    if converted_count > 0:
        print(f"Converted {converted_count} circle elements to paths")

def find_parent_and_index(root, element):
    """
    找元素的父元素和它在父元素中的索引
    
    Args:
        root: XML树的根元素
        element: 要查找的元素
        
    Returns:
        tuple: (parent_element, index) 或 (None, -1)
    """
    for parent in root.iter():
        if element in list(parent):
            return parent, list(parent).index(element)
    return None, -1

def flatten_nested_g(element, root, parent_tx=0, parent_ty=0):
    """
    递归处理嵌套的g元素，合并变换并移除不必要的g元素
    
    Args:
        element: 当前处理的元素
        root: SVG的根元素
        parent_tx: 父元素的x变换值
        parent_ty: 父元素的y变换值
    """
    # 处理当前元素的变换
    current_tx, current_ty = parent_tx, parent_ty
    
    # 处理g元素的变换
    if element.tag.endswith('}g') or element.tag == 'g':
        transform = element.get('transform')
        if transform:
            translation = extract_translate_values(transform)
            if translation:
                tx, ty = translation
                current_tx += tx
                current_ty += ty
                # 移除transform属性
                element.attrib.pop('transform')
    
    # 如果是路径元素，应用累积的变换
    if element.tag.endswith('}path') or element.tag == 'path':
        process_element(element, current_tx, current_ty)
    
    # 处理所有子元素
    for child in list(element):
        # 递归处理子元素，传递累积的变换值
        flatten_nested_g(child, root, current_tx, current_ty)

def extract_paths(root):
    """
    提取SVG中的所有路径元素
    
    Args:
        root: SVG的根元素
        
    Returns:
        list: 路径元素列表的深拷贝
    """
    paths = []
    for path in root.findall('.//path') + root.findall('.//{http://www.w3.org/2000/svg}path'):
        # 创建新的path元素
        new_path = ET.Element('path')
        # 复制所有属性
        for key, value in path.attrib.items():
            new_path.set(key, value)
        paths.append(new_path)
    return paths

def apply_paths(source_path, pattern, layer_position='top'):
    """
    将源SVG文件中的路径应用到匹配模式的所有文件上
    
    Args:
        source_path (str): 源SVG文件路径
        pattern (str): 目标文件匹配模
        layer_position (str): 'top' 或 'bottom'，决定新路径添加的位置
    """
    # 解析源文件
    source_tree = ET.parse(source_path)
    source_root = source_tree.getroot()
    
    # 提取路径
    paths = extract_paths(source_root)
    print(f"Extracted {len(paths)} paths from {source_path}")
    
    # 获取目标文件列表
    if isinstance(pattern, list):  # 如果pattern是文件列表
        target_files = pattern
    else:  # 果pattern是通配符模式
        target_files = glob.glob(pattern)
        
    if not target_files:
        print(f"No files found matching pattern: {pattern}")
        return
    
    print(f"Found {len(target_files)} matching files")
    print(f"Applying paths at {layer_position} layer")
    
    # 处理每个目标文件
    for target_file in target_files:
        try:
            # 跳过源文件
            if os.path.abspath(target_file) == os.path.abspath(source_path):
                print(f"Skipping source file: {target_file}")
                continue
                
            print(f"Processing {target_file}...")
            
            # 解析目标文件
            tree = ET.parse(target_file)
            root = tree.getroot()
            
            # 找到SVG元素可能有命名空间）
            svg = root
            if not (svg.tag.endswith('svg') or svg.tag == 'svg'):
                svg = root.find('.//{http://www.w3.org/2000/svg}svg') or root.find('.//svg')
                if svg is None:
                    print(f"Warning: No SVG element found in {target_file}")
                    continue
            
            # 添加路径到目标文件
            for path in paths:
                if layer_position == 'bottom':
                    # 在开头插入路
                    svg.insert(0, ET.fromstring(ET.tostring(path)))
                else:  # 'top'
                    # 在末尾添加路径
                    svg.append(ET.fromstring(ET.tostring(path)))
            
            # 保存修改后的文件
            with open(target_file, 'w', encoding='utf-8') as f:
                ET.register_namespace("", "http://www.w3.org/2000/svg")
                xml_str = ET.tostring(root, encoding='unicode')
                f.write(xml_str)
            
            print(f"Successfully processed: {target_file}")
            
        except Exception as e:
            print(f"Failed to process {target_file}: {str(e)}")

def convert_circles_to_paths(input_path, output_path):
    """将SVG文件中的圆形转换为路径"""
    tree = ET.parse(input_path)
    root = tree.getroot()
    convert_circles(root)  # 使用已有的convert_circles函数
    
    with open(output_path, 'w', encoding='utf-8') as f:
        ET.register_namespace("", "http://www.w3.org/2000/svg")
        xml_str = ET.tostring(root, encoding='unicode')
        f.write(xml_str)

def get_transform_matrix(transform_str):
    """解析变换字符串返回变换矩阵"""
    if not transform_str:
        return [1, 0, 0, 1, 0, 0]
    
    # 首先尝试匹配完整的matrix变换
    matrix_match = re.search(r'matrix\(([-\d.,\s]+)\)', transform_str)
    if matrix_match:
        values = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', matrix_match.group(1))]
        if len(values) == 6:
            return values
    
    # 如果不是matrix，则处理其他变换
    matrix = [1, 0, 0, 1, 0, 0]
    transforms = re.findall(r'(\w+)\s*\(([-\d.,\s]+)\)', transform_str)
    
    for transform_type, params in transforms:
        values = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', params)]
        
        if transform_type == 'translate':
            tx = values[0]
            ty = values[1] if len(values) > 1 else 0
            translation = [1, 0, 0, 1, tx, ty]
            matrix = multiply_matrices(translation, matrix)
            
        elif transform_type == 'scale':
            sx = values[0]
            sy = values[1] if len(values) > 1 else sx
            scale = [sx, 0, 0, sy, 0, 0]
            matrix = multiply_matrices(scale, matrix)
            
        elif transform_type == 'rotate':
            angle = math.radians(values[0])
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            if len(values) > 2:  # 带中心点的旋转
                cx, cy = values[1], values[2]
                t1 = [1, 0, 0, 1, cx, cy]
                r = [cos_a, sin_a, -sin_a, cos_a, 0, 0]
                t2 = [1, 0, 0, 1, -cx, -cy]
                matrix = multiply_matrices(multiply_matrices(multiply_matrices(t1, r), t2), matrix)
            else:
                rotation = [cos_a, sin_a, -sin_a, cos_a, 0, 0]
                matrix = multiply_matrices(rotation, matrix)
    
    return matrix

def multiply_matrices(m1, m2):
    """矩阵乘法 - 需要修正"""
    # SVG 变换矩阵是 3x3 矩阵的简化形式：
    # [a c e]   [m1[0] m1[2] m1[4]]
    # [b d f] = [m1[1] m1[3] m1[5]]
    # [0 0 1]   [0     0     1    ]
    return [
        m2[0]*m1[0] + m2[2]*m1[1],          # a
        m2[1]*m1[0] + m2[3]*m1[1],          # b
        m2[0]*m1[2] + m2[2]*m1[3],          # c
        m2[1]*m1[2] + m2[3]*m1[3],          # d
        m2[0]*m1[4] + m2[2]*m1[5] + m2[4],  # e
        m2[1]*m1[4] + m2[3]*m1[5] + m2[5]   # f
    ]

def get_accumulated_transform(element):
    """获取元素的累积变换矩阵"""
    transforms = []
    current = element
    
    # 从内到外收集变换
    while current is not None:
        transform = current.get('transform')
        if transform:
            transforms.append(transform)  # 添加到列表末尾
        current = current.getparent()
    
    # print(f"transforms list: {transforms}")
    # 从外到内应用变换（反向遍历）
    matrix = [1, 0, 0, 1, 0, 0]  # 单位矩阵
    
    for transform in reversed(transforms):
        matrix = multiply_matrices(get_transform_matrix(transform), matrix)

    # print(f"accumulated matrix: {matrix}")
    
    return matrix

def transform_point(point, matrix):
    """使用变换矩阵变换点坐标"""
    x, y = point
    return (
        matrix[0] * x + matrix[2] * y + matrix[4],
        matrix[1] * x + matrix[3] * y + matrix[5]
    )

def process_path(path, matrix):
    """处理单个路径元素的变换"""
    d = path.get('d', '')
    if not d:
        return
    
    commands = re.findall(r'([A-Za-z])([^A-Za-z]*)', d)
    new_d = []
    current_pos = [0, 0]
    start_pos = None
    last_control = None
    first_command = True
    
    for cmd, params in commands:
        # if cmd in 'mM':
        #     print(f"\nProcessing command: {cmd}, first_command: {first_command}, with params: {params}")
        params = [float(p) for p in re.findall(r'[-+]?\d*\.?\d+', params)]
        is_relative = cmd.islower()
        original_cmd = cmd  # 保存原始命令，用于保持命令类型
        
        if cmd in 'mM':
            for i in range(0, len(params), 2):
                x, y = params[i:i+2]
                if is_relative:
                    x += current_pos[0]
                    y += current_pos[1]
                new_x, new_y = transform_point((x, y), matrix)
                
                if first_command:
                    new_d.append(f"M{new_x:.3f},{new_y:.3f}")  # 第一个命令总是大写M
                    first_command = False
                else:
                    # 严格保持原始命令的相对/绝对性质
                    cmd_char = original_cmd if not first_command else 'M'
                    if is_relative:
                        new_d.append(f"{cmd_char}{new_x-current_pos[0]:.3f},{new_y-current_pos[1]:.3f}")
                    else:
                        new_d.append(f"{new_x:.3f},{new_y:.3f}")
                
                current_pos = [new_x, new_y]
                if start_pos is None:
                    start_pos = [new_x, new_y]

            # print(f"original_cmd: {original_cmd}, cmd_char: {cmd_char}, {params} >>>>>>>>>")
            # print(f"original_cmd: {original_cmd}, cmd_char: {cmd_char}, {new_d} <<<<<<<<<")
        
        elif cmd in 'lL':
            for i in range(0, len(params), 2):
                x, y = params[i:i+2]
                if is_relative:
                    x += current_pos[0]
                    y += current_pos[1]
                new_x, new_y = transform_point((x, y), matrix)
                if is_relative:
                    new_d.append(f"{original_cmd}{new_x-current_pos[0]:.3f},{new_y-current_pos[1]:.3f}")
                else:
                    new_d.append(f"{original_cmd}{new_x:.3f},{new_y:.3f}")
                current_pos = [new_x, new_y]
        
        elif cmd in 'hH':
            for x in params:
                if is_relative:
                    x += current_pos[0]
                y = current_pos[1]
                new_x, new_y = transform_point((x, y), matrix)
                if is_relative:
                    new_d.append(f"l{new_x-current_pos[0]:.3f},{new_y-current_pos[1]:.3f}")
                else:
                    new_d.append(f"L{new_x:.3f},{new_y:.3f}")
                current_pos = [new_x, new_y]
        
        elif cmd in 'vV':
            for y in params:
                if is_relative:
                    y += current_pos[1]
                x = current_pos[0]
                new_x, new_y = transform_point((x, y), matrix)
                if is_relative:
                    new_d.append(f"l{new_x-current_pos[0]:.3f},{new_y-current_pos[1]:.3f}")
                else:
                    new_d.append(f"L{new_x:.3f},{new_y:.3f}")
                current_pos = [new_x, new_y]
        
        elif cmd in 'cC':
            for i in range(0, len(params), 6):
                x1, y1, x2, y2, x, y = params[i:i+6]
                if is_relative:
                    x1 += current_pos[0]
                    y1 += current_pos[1]
                    x2 += current_pos[0]
                    y2 += current_pos[1]
                    x += current_pos[0]
                    y += current_pos[1]
                
                new_x1, new_y1 = transform_point((x1, y1), matrix)
                new_x2, new_y2 = transform_point((x2, y2), matrix)
                new_x, new_y = transform_point((x, y), matrix)
                
                if is_relative:
                    new_d.append(f"c{new_x1-current_pos[0]:.3f},{new_y1-current_pos[1]:.3f} "
                               f"{new_x2-current_pos[0]:.3f},{new_y2-current_pos[1]:.3f} "
                               f"{new_x-current_pos[0]:.3f},{new_y-current_pos[1]:.3f}")
                else:
                    new_d.append(f"C{new_x1:.3f},{new_y1:.3f} {new_x2:.3f},{new_y2:.3f} {new_x:.3f},{new_y:.3f}")
                current_pos = [new_x, new_y]
                last_control = [new_x2, new_y2]
        
        elif cmd in 'zZ':
            new_d.append('Z')
            if start_pos:
                current_pos = start_pos.copy()
            first_command = True
    
    path.set('d', ' '.join(new_d))
    if 'transform' in path.attrib:
        path.attrib.pop('transform')

def apply_transform_to_path(svg_path, output_path=None):
    """用变换属性到路径数据并移除变换"""
    try:
        from lxml import etree as ET
        tree = ET.parse(svg_path)
        root = tree.getroot()
        
        # 处理所有路径和圆形元素
        paths = root.xpath('.//path | .//svg:path', namespaces={'svg': 'http://www.w3.org/2000/svg'})
        circles = root.xpath('.//circle | .//svg:circle', namespaces={'svg': 'http://www.w3.org/2000/svg'})
        
        # 处理路径
        for path in paths:
            matrix = get_accumulated_transform(path)
            process_path(path, matrix)
        
        # 处理圆形
        for circle in circles:
            matrix = get_accumulated_transform(circle)
            process_circle(circle, matrix)
            
        # 移除所有祖先元素的transform属性
        for element in root.xpath('.//*[@transform]'):
            element.attrib.pop('transform')
        
        tree.write(output_path, encoding='utf-8', xml_declaration=True, pretty_print=True)
        return True
        
    except Exception as e:
        print(f"处理文件时发生错误：{str(e)}")
        import traceback
        traceback.print_exc()
        return False

def clean_svg(svg_path, output_path=None):
    """Clean SVG file by removing XML declaration, defs elements and clip-path attributes
    
    Args:
        svg_path: Path to SVG file
        output_path: Output path (optional)
    """
    try:
        # 直接读取文件内容
        with open(svg_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 移除 XML 声明
        content = re.sub(r'<\?xml[^>]+\?>\s*', '', content)
        
        # 解析清理后的内容
        root = ET.fromstring(content)
        
        # 移除 defs 元素
        for defs in root.findall('.//defs') + root.findall('.//{http://www.w3.org/2000/svg}defs'):
            # 正确查找父元素
            for parent in root.iter():
                if defs in list(parent):
                    parent.remove(defs)
                    break
        
        # 移除 clip-path 属性
        for g in root.findall('.//g') + root.findall('.//{http://www.w3.org/2000/svg}g'):
            if 'clip-path' in g.attrib:
                del g.attrib['clip-path']
        
        # 转换回字符串，但不包含XML声明
        ET.register_namespace("", "http://www.w3.org/2000/svg")
        cleaned_content = ET.tostring(root, encoding='unicode')
        
        # 写入文件
        output_path = output_path or svg_path
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
            
        print(f"Cleaned: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error cleaning {svg_path}: {str(e)}")
        return False

def process_circle(circle, matrix):
    """处理单个圆形元素的变换
    
    Args:
        circle: 圆形元素
        matrix: 变换矩阵
    """
    # 获取当前cx和cy值
    cx = float(circle.get('cx', '0'))
    cy = float(circle.get('cy', '0'))
    
    # 应用变换矩阵到圆心坐标
    new_cx, new_cy = transform_point((cx, cy), matrix)
    
    # 更新圆形元素的属性
    circle.set('cx', f"{new_cx:.3f}")
    circle.set('cy', f"{new_cy:.3f}")
    
    # 移除transform属性
    if 'transform' in circle.attrib:
        circle.attrib.pop('transform')

def convert_relative_to_absolute(d: str) -> str:
    """将SVG路径中的相对坐标转换为绝对坐标
    
    Args:
        d: SVG路径数据字符串
        
    Returns:
        转换后的路径数据字符串，所有坐标都是绝对的
    """
    current_x = current_y = 0  # 当前位置
    subpath_start_x = subpath_start_y = 0  # 子路径起点
    new_d = []
    
    # 分割命令和参数
    commands = re.findall(r'([a-zA-Z])([^a-zA-Z]*)', d)
    
    for cmd, params in commands:
        # 解析参数为浮点数列表
        params = [float(p) for p in re.findall(r'[-+]?\d*\.?\d+', params)]
        is_relative = cmd.islower()
        upper_cmd = cmd.upper()
        
        if upper_cmd == 'M':  # 移动命令
            if is_relative and params:
                current_x += params[0]
                current_y += params[1]
            else:
                current_x = params[0]
                current_y = params[1]
            subpath_start_x = current_x
            subpath_start_y = current_y
            new_d.append(f"M{current_x:.3f},{current_y:.3f}")
            
            # 处理额外的坐标对
            for i in range(2, len(params), 2):
                if is_relative:
                    current_x += params[i]
                    current_y += params[i + 1]
                else:
                    current_x = params[i]
                    current_y = params[i + 1]
                new_d.append(f"L{current_x:.3f},{current_y:.3f}")
                
        elif upper_cmd == 'L':  # 直线命令
            for i in range(0, len(params), 2):
                if is_relative:
                    current_x += params[i]
                    current_y += params[i + 1]
                else:
                    current_x = params[i]
                    current_y = params[i + 1]
                new_d.append(f"L{current_x:.3f},{current_y:.3f}")
                
        elif upper_cmd == 'H':  # 水平线
            for x in params:
                if is_relative:
                    current_x += x
                else:
                    current_x = x
                new_d.append(f"L{current_x:.3f},{current_y:.3f}")
                
        elif upper_cmd == 'V':  # 垂直线
            for y in params:
                if is_relative:
                    current_y += y
                else:
                    current_y = y
                new_d.append(f"L{current_x:.3f},{current_y:.3f}")
                
        elif upper_cmd == 'C':  # 三次贝塞尔曲线
            for i in range(0, len(params), 6):
                x1, y1, x2, y2, x, y = params[i:i+6]
                if is_relative:
                    x1 += current_x
                    y1 += current_y
                    x2 += current_x
                    y2 += current_y
                    x += current_x
                    y += current_y
                current_x = x
                current_y = y
                new_d.append(f"C{x1:.3f},{y1:.3f} {x2:.3f},{y2:.3f} {x:.3f},{y:.3f}")
                
        elif upper_cmd == 'S':  # 平滑三次贝塞尔曲线
            for i in range(0, len(params), 4):
                x2, y2, x, y = params[i:i+4]
                if is_relative:
                    x2 += current_x
                    y2 += current_y
                    x += current_x
                    y += current_y
                current_x = x
                current_y = y
                new_d.append(f"S{x2:.3f},{y2:.3f} {x:.3f},{y:.3f}")
                
        elif upper_cmd == 'Q':  # 二次贝塞尔曲线
            for i in range(0, len(params), 4):
                x1, y1, x, y = params[i:i+4]
                if is_relative:
                    x1 += current_x
                    y1 += current_y
                    x += current_x
                    y += current_y
                current_x = x
                current_y = y
                new_d.append(f"Q{x1:.3f},{y1:.3f} {x:.3f},{y:.3f}")
                
        elif upper_cmd == 'T':  # 平滑二次贝塞尔曲线
            for i in range(0, len(params), 2):
                x, y = params[i:i+2]
                if is_relative:
                    x += current_x
                    y += current_y
                current_x = x
                current_y = y
                new_d.append(f"T{x:.3f},{y:.3f}")
                
        elif upper_cmd == 'A':  # 圆弧
            for i in range(0, len(params), 7):
                rx, ry, angle, large_arc, sweep, x, y = params[i:i+7]
                if is_relative:
                    x += current_x
                    y += current_y
                current_x = x
                current_y = y
                new_d.append(f"A{rx:.3f},{ry:.3f} {angle:.3f} {int(large_arc)},{int(sweep)} {x:.3f},{y:.3f}")
                
        elif upper_cmd == 'Z':  # 闭合路径
            current_x = subpath_start_x
            current_y = subpath_start_y
            new_d.append('Z')
            
    return ' '.join(new_d)

def convert_to_absolute(svg_path, output_path=None):
    """将SVG文件中的相对坐标转换为绝对坐标"""

    try:
        from lxml import etree as ET
        tree = ET.parse(svg_path)
        root = tree.getroot()
        
        # 处理所有路径和圆形元素
        paths = root.xpath('.//path | .//svg:path', namespaces={'svg': 'http://www.w3.org/2000/svg'})
        
        # 处理路径
        for path in paths:
            path.set('d', convert_relative_to_absolute(path.get('d', '')))
        
        tree.write(output_path, encoding='utf-8', xml_declaration=True, pretty_print=True)
        return True
        
    except Exception as e:
        print(f"处理文件时发生错误：{str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(
        description='SVG transformation tools',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # transform 命令
    transform_parser = subparsers.add_parser('translate',
        help='Transform SVG file by applying g element translations')
    transform_parser.add_argument('files', nargs='+',
                               help='Input SVG files to process')
    transform_parser.add_argument('-o', '--output',
                               help='Output folder path. If not provided, will overwrite input files')
    
    # dedup 命令
    dedup_parser = subparsers.add_parser('dedup', 
        help='Remove duplicate paths from SVG files')
    dedup_parser.add_argument('files', nargs='+',
                            help='Input SVG files to process')
    dedup_parser.add_argument('-o', '--output',
                            help='Output folder path. If not provided, will overwrite input files')
    
    # circle2path 命令
    circle2path_parser = subparsers.add_parser('circle2path',
        help='Convert circles to paths in SVG files')
    circle2path_parser.add_argument('files', nargs='+',
                                 help='Input SVG files to process')
    circle2path_parser.add_argument('-o', '--output',
                                 help='Output folder path. If not provided, will overwrite input files')
    
    # applytransformtopath command
    applytransform_parser = subparsers.add_parser('transform', 
        help='Apply transform attributes to <path> data',
        description='Calculate <path> values with transform attributes and remove transforms')
    applytransform_parser.add_argument('files', nargs='+', help='SVG files to process')
    applytransform_parser.add_argument('-o', '--output', help='Output file path')

    # convert_to_absolute command
    convert_to_absolute_parser = subparsers.add_parser('absolute', 
        help='Convert relative coordinates to absolute coordinates in SVG files',
        description='Convert relative coordinates to absolute coordinates in SVG files')
    convert_to_absolute_parser.add_argument('files', nargs='+', help='SVG files to process')
    convert_to_absolute_parser.add_argument('-o', '--output', help='Output file path')

    # clean command
    clean_parser = subparsers.add_parser('clean', 
        help='Clean SVG file',
        description='Remove all transform attributes from SVG files')
    clean_parser.add_argument('files', nargs='+', help='SVG files to process')
    clean_parser.add_argument('-r', '--recursive', action='store_true', help='Process directories recursively')
    clean_parser.add_argument('-o', '--output', help='Output directory')

    args = parser.parse_args()
    
    try:
        if args.command == 'translate':
            for file_path in args.files:
                try:
                    print(f"\nProcessing {file_path}...")
                    output_path = os.path.join(args.output, os.path.basename(file_path)) if args.output else file_path
                    if args.output:
                        os.makedirs(args.output, exist_ok=True)
                    apply_translate_from_g(file_path, output_path)
                except Exception as e:
                    print(f"Failed to process {file_path}: {str(e)}")
                    
        elif args.command == 'clean':
            for pattern in args.files:
                pattern = os.path.expanduser(pattern)
                
                if args.recursive and '**' not in pattern:
                    base_dir = os.path.dirname(pattern) or '.'
                    file_pattern = os.path.basename(pattern)
                    pattern = os.path.join(base_dir, '**', file_pattern)
                
                matching_files = glob.glob(pattern, recursive=args.recursive)
                
                if not matching_files:
                    print(f"No files found matching pattern: {pattern}")
                    continue
                
                print(f"Found {len(matching_files)} files matching pattern: {pattern}")
                for file_path in matching_files:
                    if file_path.lower().endswith('.svg'):
                        try:
                            clean_svg(file_path, args.output)
                        except Exception as e:
                            print(f"Error processing {file_path}: {str(e)}")

        elif args.command == 'dedup':
            for file_path in args.files:
                try:
                    print(f"\nProcessing {file_path}...")
                    output_path = os.path.join(args.output, os.path.basename(file_path)) if args.output else file_path
                    if args.output:
                        os.makedirs(args.output, exist_ok=True)
                    tree = ET.parse(file_path)
                    root = tree.getroot()
                    remove_duplicate_paths(root)
                    with open(output_path, 'w', encoding='utf-8') as f:
                        ET.register_namespace("", "http://www.w3.org/2000/svg")
                        xml_str = ET.tostring(root, encoding='unicode')
                        f.write(xml_str)
                except Exception as e:
                    print(f"Failed to process {file_path}: {str(e)}")
                    
        elif args.command == 'circle2path':
            for file_path in args.files:
                try:
                    print(f"\nProcessing {file_path}...")
                    output_path = os.path.join(args.output, os.path.basename(file_path)) if args.output else file_path
                    if args.output:
                        os.makedirs(args.output, exist_ok=True)
                    convert_circles_to_paths(file_path, output_path)
                except Exception as e:
                    print(f"Failed to process {file_path}: {str(e)}")
            
        elif args.command == 'transform':
            for pattern in args.files:
                pattern = os.path.expanduser(pattern)
                                
                matching_files = glob.glob(pattern, recursive=False)
                
                if not matching_files:
                    print(f"No files found matching pattern: {pattern}")
                    continue
                
                print(f"Found {len(matching_files)} files matching pattern: {pattern}")
                for file_path in matching_files:
                    if file_path.lower().endswith('.svg'):
                        try:
                            output_file = file_path
                            
                            # 确保输出目录存在
                            os.makedirs(os.path.dirname(output_file), exist_ok=True)
                            
                            print(f"\nProcessing {file_path} to {output_file}...")
                            result = apply_transform_to_path(file_path, output_file)

                            if result:
                                print(f"Successfully processed: {file_path}")
                            else:
                                print(f"Failed to process: {file_path}")
                        except Exception as e:
                            print(f"Error processing {file_path}: {str(e)}")            

        elif args.command == 'absolute':
            for pattern in args.files:
                pattern = os.path.expanduser(pattern)
                                
                matching_files = glob.glob(pattern, recursive=False)
                
                if not matching_files:
                    print(f"No files found matching pattern: {pattern}")
                    continue
                
                print(f"Found {len(matching_files)} files matching pattern: {pattern}")
                for file_path in matching_files:
                    if file_path.lower().endswith('.svg'):
                        try:
                            output_file = file_path
                            
                            # 确保输出目录存在
                            os.makedirs(os.path.dirname(output_file), exist_ok=True)
                            
                            print(f"\nProcessing {file_path} to {output_file}...")
                            result = convert_to_absolute(file_path, output_file)

                            if result:
                                print(f"Successfully processed: {file_path}")
                            else:
                                print(f"Failed to process: {file_path}")
                        except Exception as e:
                            print(f"Error processing {file_path}: {str(e)}")            

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()