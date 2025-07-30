import os
import subprocess
import json
import tempfile
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET
import argparse

class SVGCompressor:
    """SVG文件压缩器，使用SVGO进行优化压缩"""
    
    def __init__(self):
        # SVGO配置
        self.svgo_config = {
            "multipass": True,  # 多次优化以获得更好的压缩效果
            "plugins": [
                {
                    "name": "preset-default",
                    "params": {
                        "overrides": {
                            # 保持重要属性
                            "removeViewBox": False,
                            "removeHiddenElems": False,
                            "removeUselessDefs": False,
                            "removeUnknownsAndDefaults": {
                                "keepRoleAttr": True,
                                "keepAriaLabel": True,
                            },
                            # 保持class属性
                            "keepClassAttr": True,
                            # 不移除XML声明
                            "removeXMLProcInst": False,
                        }
                    }
                },
                # 清理和简化路径
                {
                    "name": "cleanupListOfValues"
                },
                {
                    "name": "convertPathData"
                },
                # 合并路径
                {
                    "name": "mergePaths"
                },
                # 将样式转换为属性
                {
                    "name": "convertStyleToAttrs"
                },
                # 移除注释
                {
                    "name": "removeComments"
                },
                # 移除空属性
                {
                    "name": "removeEmptyAttrs"
                },
                # 移除空文本
                {
                    "name": "removeEmptyText"
                },
                # 移除空容器
                {
                    "name": "removeEmptyContainers"
                },
                # 缩短颜色值
                {
                    "name": "convertColors"
                },
                # 折叠无用的组
                {
                    "name": "collapseGroups"
                }
            ]
        }
        self.path_hash_map = {}  # 用于存储路径的哈希值和对应的路径元素
        self.removed_count = 0
        self.debug_info = []

    def _check_svgo_installation(self):
        """检查SVGO是否已安装"""
        try:
            subprocess.run(['svgo', '--version'], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
            return True
        except FileNotFoundError:
            return False

    def _install_svgo(self):
        """安装SVGO"""
        try:
            subprocess.run(['npm', 'install', '-g', 'svgo'], 
                         check=True,
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError as e:
            print(f"安装SVGO失败: {e}")
            return False
        except FileNotFoundError:
            print("错误: 需要安装Node.js和npm才能安装SVGO")
            return False

    def _ensure_svgo(self):
        """确保SVGO可用"""
        if not self._check_svgo_installation():
            print("SVGO未安装，正在尝试安装...")
            if not self._install_svgo():
                raise RuntimeError("无法安装SVGO，请确保已安装Node.js和npm")

    def compress_file(self, input_path, output_path=None):
        """
        压缩单个SVG文件
        
        Args:
            input_path (str): 输入SVG文件路径
            output_path (str, optional): 输出SVG文件路径。如果未指定，将覆盖原文件
            
        Returns:
            tuple: (是否成功, 原始大小, 压缩后大小)
        """
        self._ensure_svgo()
        
        if output_path is None:
            output_path = input_path
            
        try:
            # 创建临时配置文件，使用 .config.json 作为后缀
            with tempfile.NamedTemporaryFile('w', suffix='.config.json', delete=False) as f:
                json.dump(self.svgo_config, f, indent=2)  # 使用类中已定义的配置
                config_path = f.name

            try:
                # 修改 SVGO 命令行参数
                result = subprocess.run([
                    'svgo',
                    '--config', config_path,  # 使用 --config 而不是 --configFile
                    input_path,  # 移除 -i 参数
                    '-o', output_path
                ], check=True, capture_output=True, text=True)
                
                # 获取文件大小
                original_size = os.path.getsize(input_path)
                compressed_size = os.path.getsize(output_path)
                
                return True, original_size, compressed_size
                
            finally:
                # 清理临时配置文件
                try:
                    os.unlink(config_path)
                except:
                    pass
                
        except subprocess.CalledProcessError as e:
            print(f"压缩失败: {e.stderr}")
            return False, 0, 0
        except Exception as e:
            print(f"压缩失败: {str(e)}")
            return False, 0, 0

    def compress_folder(self, input_folder, output_folder=None, recursive=True):
        """
        压缩文件夹中的所有SVG文件
        
        Args:
            input_folder (str): 输入文件夹路径
            output_folder (str, optional): 输出文件夹路径。如果未指定，将覆盖原文件
            recursive (bool): 是否递归处理子文件夹
            
        Returns:
            dict: 压缩统计信息
        """
        self._ensure_svgo()
        
        stats = {
            'total_files': 0,
            'successful': 0,
            'failed': 0,
            'original_size': 0,
            'compressed_size': 0
        }
        
        # 如果指定了输出文件夹，确保它存在
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
            
            # 压缩文件
            success, orig_size, comp_size = self.compress_file(file_path, out_path)
            
            if success:
                stats['successful'] += 1
                stats['original_size'] += orig_size
                stats['compressed_size'] += comp_size
            else:
                stats['failed'] += 1
        
        # 遍历文件夹
        if recursive:
            for root, _, files in os.walk(input_folder):
                for file in files:
                    process_file(os.path.join(root, file))
        else:
            for file in os.listdir(input_folder):
                process_file(os.path.join(input_folder, file))
        
        return stats

    def compress(self, svg_content):
        # 解析SVG
        root = ET.fromstring(svg_content)
        self._remove_duplicate_paths(root)
        
        # 使用紧凑的格式输出
        ET.register_namespace("", "http://www.w3.org/2000/svg")
        
        # 移除所有不必要的空白
        self._remove_whitespace(root)
        
        # 使用最紧凑的方式序列化
        return ET.tostring(root, encoding='unicode', method='xml', short_empty_elements=True)
    
    def _remove_whitespace(self, element):
        """递归移除元素间的空白文本"""
        if element.text and not element.text.strip():
            element.text = None
        if element.tail and not element.tail.strip():
            element.tail = None
        for child in element:
            self._remove_whitespace(child)
    
    def _remove_duplicate_paths(self, root):
        self.path_hash_map.clear()
        self.removed_count = 0
        self.debug_info = []
        
        # 查找所有路径元素，反向遍历以保持最上层的路径
        paths = root.findall(".//*[@d]")
        total_paths = len(paths)
        paths = list(reversed(paths))
        
        for path in paths:
            path_key = self._create_path_hash(path)
            
            if path_key in self.path_hash_map:
                # 记录要删除的路径信息
                self.debug_info.append({
                    'action': 'removed',
                    'path_data': path.get('d', '')[:50] + '...',
                    'fill': path.get('fill', ''),
                    'parent_tag': path.getparent().tag if path.getparent() is not None else 'None'
                })
                # 移除重复路径
                parent = path.getparent()
                if parent is not None:
                    parent.remove(path)
                    self.removed_count += 1
            else:
                # 保存新路径
                self.path_hash_map[path_key] = path
                self.debug_info.append({
                    'action': 'kept',
                    'path_data': path.get('d', '')[:50] + '...',
                    'fill': path.get('fill', ''),
                    'parent_tag': path.getparent().tag if path.getparent() is not None else 'None'
                })
        
        return total_paths
    
    def _create_path_hash(self, path):
        """创建路径的唯一标识"""
        attributes = [
            path.get('d', ''),
            path.get('fill', ''),
            path.get('fill-rule', ''),
            path.get('fill-opacity', '')
        ]
        return hash(tuple(attributes))

def main():
    parser = argparse.ArgumentParser(
        description='SVG compression tool',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('command',
                       choices=['compress'],
                       help='Command to execute')
    
    parser.add_argument('files', nargs='+',
                       help='Input SVG files to process')
    
    parser.add_argument('-o', '--output',
                       help='Output folder path. If not provided, will overwrite input files')
    
    args = parser.parse_args()
    
    compressor = SVGCompressor()
    
    if args.command == 'compress':
        for file_path in args.files:
            try:
                print(f"\nProcessing {file_path}...")
                output_path = os.path.join(args.output, os.path.basename(file_path)) if args.output else file_path
                if args.output:
                    os.makedirs(args.output, exist_ok=True)
                    
                success, orig_size, comp_size = compressor.compress_file(file_path, output_path)
                if success:
                    reduction = (1 - comp_size/orig_size) * 100
                    print(f"Successfully compressed: {file_path}")
                    print(f"Original size: {orig_size:,} bytes")
                    print(f"Compressed size: {comp_size:,} bytes")
                    print(f"Reduction: {reduction:.1f}%")
                else:
                    print(f"Failed to compress: {file_path}")
            except Exception as e:
                print(f"Failed to process {file_path}: {str(e)}")

if __name__ == "__main__":
    main() 