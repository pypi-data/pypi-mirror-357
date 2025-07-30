import os
import cairosvg
from PIL import Image
import io
import argparse

class SVGConverter:
    """SVG文件转换器，支持SVG转PNG"""
    
    def __init__(self):
        pass

    def svg_to_png(self, input_path, output_path=None, scale=1.0, background_color=None):
        """
        将SVG文件转换为PNG文件
        
        Args:
            input_path (str): 输入SVG文件路径
            output_path (str, optional): 输出PNG文件路径。如果未指定，将使用相同文件名但扩展名改为.png
            scale (float): 输出图像的缩放比例
            background_color (str, optional): 背景颜色，默认为None（透明）
            
        Returns:
            bool: 转换是否成功
        """
        try:
            # 如果未指定输出路径，则使用输入路径但改变扩展名
            if output_path is None:
                output_path = os.path.splitext(input_path)[0] + '.png'
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # 读取SVG文件
            with open(input_path, 'rb') as svg_file:
                svg_data = svg_file.read()
            
            # 转换为PNG（注意这里background_color可以为None）
            png_data = cairosvg.svg2png(
                bytestring=svg_data,
                scale=scale,
                background_color=background_color
            )
            
            # 使用PIL处理图像并保存
            image = Image.open(io.BytesIO(png_data))
            
            # 确保图像模式为RGBA以支持透明度
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
                
            # 移除transparency参数，因为RGBA模式本身就支持透明度
            image.save(output_path, 'PNG')
            
            print(f"成功将 {input_path} 转换为 {output_path}")
            return True
            
        except Exception as e:
            print(f"文件 {input_path} 转换失败: {str(e)}")
            return False

    def convert_folder(self, input_folder, output_folder=None, recursive=True, scale=1.0, background_color=None):
        """
        转换文件夹中的所有SVG文件为PNG
        
        Args:
            input_folder (str): 输入文件夹路径
            output_folder (str, optional): 输出文件夹路径。如果未指定，将在原文件夹中创建PNG文件
            recursive (bool): 是否递归处理子文件夹
            scale (float): 输出图像的缩放比例
            background_color (str, optional): 背景颜色，默认为None（透明）
            
        Returns:
            dict: 转换���计信息
        """
        stats = {
            'total_files': 0,
            'successful': 0,
            'failed': 0,
            'failed_files': []
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
                out_path = os.path.join(output_folder, os.path.splitext(rel_path)[0] + '.png')
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
            else:
                out_path = os.path.splitext(file_path)[0] + '.png'
            
            # 转换文件
            if self.svg_to_png(file_path, out_path, scale, background_color):
                stats['successful'] += 1
            else:
                stats['failed'] += 1
                stats['failed_files'].append(file_path)
        
        # 遍历文件夹
        if recursive:
            for root, _, files in os.walk(input_folder):
                for file in files:
                    process_file(os.path.join(root, file))
        else:
            for file in os.listdir(input_folder):
                process_file(os.path.join(input_folder, file))
        
        # 如果有失败的文件，输出它们的列表
        if stats['failed'] > 0:
            print("\n失败的文件列表:")
            for failed_file in stats['failed_files']:
                print(f"- {failed_file}")
        
        return stats

def main():
    parser = argparse.ArgumentParser(
        description='SVG to PNG converter',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('command',
                       choices=['convert'],
                       help='Command to execute')
    
    parser.add_argument('files', nargs='+',
                       help='Input SVG files to process')
    
    parser.add_argument('-o', '--output',
                       help='Output folder path. If not provided, will create PNG files in the same folder')
    
    parser.add_argument('--scale',
                       type=float,
                       default=1.0,
                       help='Output image scale (default: 1.0)')
    
    parser.add_argument('--background',
                       help='Background color (default: transparent)')
    
    args = parser.parse_args()
    
    converter = SVGConverter()
    
    if args.command == 'convert':
        for file_path in args.files:
            try:
                print(f"\nProcessing {file_path}...")
                if args.output:
                    os.makedirs(args.output, exist_ok=True)
                    output_path = os.path.join(args.output, 
                                             os.path.splitext(os.path.basename(file_path))[0] + '.png')
                else:
                    output_path = os.path.splitext(file_path)[0] + '.png'
                    
                success = converter.svg_to_png(
                    file_path,
                    output_path,
                    args.scale,
                    args.background
                )
                if success:
                    print(f"Successfully converted: {file_path} -> {output_path}")
                else:
                    print(f"Failed to convert: {file_path}")
            except Exception as e:
                print(f"Failed to process {file_path}: {str(e)}")

if __name__ == "__main__":
    main() 