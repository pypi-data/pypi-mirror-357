#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import argparse
import re
from typing import List, Dict, Any, Optional
import os
from qcloud_cos import CosConfig, CosS3Client, CosServiceError, CosClientError

class COSUploader:
    """COS 上传器"""
    
    def __init__(
        self,
        service_root: str,
        cos_region: str,
        cos_secret_id: str,
        cos_secret_key: str,
        cos_bucket: str,
        cos_token: Optional[str] = None,
        cos_scheme: str = "https"
    ):
        """初始化 COS 上传器
        
        Args:
            service_root: 服务根路径
            cos_region: COS 区域
            cos_secret_id: 密钥 ID
            cos_secret_key: 密钥
            cos_bucket: 存储桶名称
            cos_token: 令牌（可选）
            cos_scheme: 协议（默认为 https）
        """
        self.service_root = service_root
        self._config = CosConfig(
            Region=cos_region,
            SecretId=cos_secret_id,
            SecretKey=cos_secret_key,
            Token=cos_token,
            Scheme=cos_scheme,
        )
        self._client = CosS3Client(self._config)
        self._bucket = cos_bucket
        self._region = cos_region
    
    def copy_file(self, src_path: str, dest_path: str) -> bool:
        """复制 COS 中的文件
        
        Args:
            src_path: 源文件路径（以 / 开头）
            dest_path: 目标文件路径（以 / 开头）
            
        Returns:
            bool: 是否复制成功
        """
        try:
            # 移除开头的 /
            src_key = src_path[1:] if src_path.startswith('/') else src_path
            dest_key = dest_path[1:] if dest_path.startswith('/') else dest_path
            
            # 执行复制
            response = self._client.copy_object(
                Bucket=self._bucket,
                Key=dest_key,
                CopySource={
                    'Bucket': self._bucket,
                    'Key': src_key,
                    'Region': self._region
                }
            )
            print(f'File copied from {src_path} to {dest_path}')
            return True
            
        except (CosServiceError, CosClientError) as e:
            print(f'Error copying file from {src_path} to {dest_path}: {str(e)}')
            return False

class MockCOSUploader:
    """模拟的 COS 上传器（用于测试）"""
    
    def __init__(self):
        self.copied_files = []
    
    def copy_file(self, src_path: str, dest_path: str) -> bool:
        """模拟复制文件
        
        Args:
            src_path: 源文件路径
            dest_path: 目标文件路径
            
        Returns:
            bool: 是否复制成功
        """
        print(f"[MOCK] Copying file from {src_path} to {dest_path}")
        self.copied_files.append((src_path, dest_path))
        return True

class COSPathProcessor:
    """COS 路径处理器"""
    
    def __init__(self, cos_uploader: Optional[Any] = None, search_pattern: str = r'^/story/.*'):
        """初始化处理器
        
        Args:
            cos_uploader: COS 上传器实例，如果为 None 则使用模拟上传器
            search_pattern: 搜索模式的正则表达式
        """
        self.cos_uploader = cos_uploader if cos_uploader else MockCOSUploader()
        self.story_paths = []
        self.search_pattern = search_pattern
    
    def _is_story_path(self, value: str) -> bool:
        """检查值是否是故事路径
        
        Args:
            value: 要检查的值
            
        Returns:
            bool: 是否是故事路径
        """
        if not isinstance(value, str):
            return False
        return bool(re.match(self.search_pattern, value))
    
    def _process_value(self, value: Any) -> None:
        """处理单个值
        
        Args:
            value: 要处理的值
        """
        if isinstance(value, dict):
            self._find_story_paths(value)
        elif isinstance(value, list):
            for item in value:
                self._process_value(item)
        elif self._is_story_path(value):
            self.story_paths.append(value)
    
    def _find_story_paths(self, data: Dict[str, Any]) -> None:
        """在字典中查找故事路径
        
        Args:
            data: 要处理的字典数据
        """
        for value in data.values():
            self._process_value(value)
    
    def process_json_file(self, json_file: str) -> List[str]:
        """处理 JSON 文件
        
        Args:
            json_file: JSON 文件路径
            
        Returns:
            List[str]: 找到的故事路径列表
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.story_paths = []
            self._find_story_paths(data)
            return self.story_paths
            
        except Exception as e:
            print(f"Error processing JSON file: {e}")
            return []
    
    def copy_files(self, story_paths: List[str], dest_prefix: str) -> bool:
        """复制文件到新路径
        
        Args:
            story_paths: 故事路径列表
            dest_prefix: 目标路径前缀
            
        Returns:
            bool: 是否全部复制成功
        """
        success = True
        for src_path in story_paths:
            try:
                # 构建目标路径
                dest_path = os.path.join(dest_prefix, os.path.basename(src_path))
                # 确保路径以 / 开头
                if not dest_path.startswith('/'):
                    dest_path = '/' + dest_path
                
                # 复制文件
                if not self.cos_uploader.copy_file(src_path, dest_path):
                    print(f"Failed to copy file: {src_path}")
                    success = False
                    
            except Exception as e:
                print(f"Error copying file {src_path}: {e}")
                success = False
                
        return success

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Process story paths in JSON file')
    parser.add_argument('json_file', help='Input JSON file path')
    parser.add_argument('command', choices=['detect', 'copy'], 
                      help='Command to execute: detect (find paths) or copy (copy files)')
    parser.add_argument('--dest', help='Destination prefix for copy command', default='')
    parser.add_argument('--pattern', help='Search pattern (regular expression), default: ^/story/.*', 
                      default=r'^/story/.*')
    
    # COS 配置参数
    parser.add_argument('--service-root', help='COS service root')
    parser.add_argument('--region', help='COS region')
    parser.add_argument('--secret-id', help='COS secret ID')
    parser.add_argument('--secret-key', help='COS secret key')
    parser.add_argument('--bucket', help='COS bucket name')
    parser.add_argument('--mock', action='store_true', help='Use mock COS uploader')
    
    args = parser.parse_args()
    
    # 创建处理器
    if args.command == 'copy' and not args.mock:
        # 从命令行参数或环境变量获取 COS 配置
        service_root = args.service_root or os.environ.get('QCLOUD_SERVICE_ROOT')
        region = args.region or os.environ.get('QCLOUD_REGION')
        secret_id = args.secret_id or os.environ.get('QCLOUD_SECRET_ID')
        secret_key = args.secret_key or os.environ.get('QCLOUD_SECRET_KEY')
        bucket = args.bucket or os.environ.get('QCLOUD_BUCKET')
        
        # 检查必要的 COS 参数
        if not all([service_root, region, secret_id, secret_key, bucket]):
            print("Error: All COS parameters are required for copy command when not using mock uploader")
            print("Please provide either command line arguments:")
            print("  --service-root, --region, --secret-id, --secret-key, --bucket")
            print("Or environment variables:")
            print("  QCLOUD_SERVICE_ROOT, QCLOUD_REGION, QCLOUD_SECRET_ID, QCLOUD_SECRET_KEY, QCLOUD_BUCKET")
            print("Or use --mock to use mock uploader")
            return
            
        # 创建实际的 COS 上传器
        cos_uploader = COSUploader(
            service_root=service_root,
            cos_region=region,
            cos_secret_id=secret_id,
            cos_secret_key=secret_key,
            cos_bucket=bucket
        )
        processor = COSPathProcessor(cos_uploader=cos_uploader, search_pattern=args.pattern)
    else:
        # 使用模拟上传器
        processor = COSPathProcessor(search_pattern=args.pattern)
    
    # 处理 JSON 文件
    story_paths = processor.process_json_file(args.json_file)
    
    if args.command == 'detect':
        # 打印找到的路径
        if story_paths:
            print("\nFound story paths:")
            for path in story_paths:
                print(path)
        else:
            print("\nNo story paths found.")
            
    elif args.command == 'copy':
        # 检查目标路径
        if not args.dest:
            print("Error: --dest argument is required for copy command")
            return
            
        # 复制文件
        print(f"\nCopying files to {args.dest}...")
        if processor.copy_files(story_paths, args.dest):
            print("All files copied successfully")
        else:
            print("Some files failed to copy")

if __name__ == '__main__':
    main()
