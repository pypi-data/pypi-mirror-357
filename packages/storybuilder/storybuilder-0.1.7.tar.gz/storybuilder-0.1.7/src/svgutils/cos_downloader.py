# -*- coding=utf-8
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging
import os
import argparse
import glob

class COSDownloader:
    """用于从腾讯云COS下载文件的工具类"""
    
    def __init__(self, client):
        """
        初始化COS下载器
        
        Args:
            client: CosS3Client实例
        """
        # 设置日志级别
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        
        # 直接使用传入的client实例，不需要重新创建配置
        self.client = client
        
    def list_files(self, bucket, prefix='', delimiter=''):
        """
        列出存储桶中的文件
        
        Args:
            bucket (str): 存储桶名称，格式为 BucketName-APPID
            prefix (str): 要列出的目录前缀
            delimiter (str): 分隔符，用于列出特定目录

        Returns:
            list: 文件信息列表
        """
        marker = ""
        files = []
        
        while True:
            try:
                response = self.client.list_objects(
                    Bucket=bucket,
                    Prefix=prefix,
                    Delimiter=delimiter,
                    Marker=marker,
                    MaxKeys=1000  # 每次请求的最大数量
                )
                
                print(f"Listing files with prefix: {prefix}")
                
                # 处理文件列表
                if 'Contents' in response:
                    files.extend(response['Contents'])
                    print(f"Found {len(response['Contents'])} files in current batch")
                
                # 检查是否还有更多文件
                if response.get('IsTruncated') == 'false':
                    break
                    
                marker = response.get('NextMarker', '')
                if not marker:
                    break
                    
            except Exception as e:
                print(f"Error listing files: {str(e)}")
                break
        
        print(f"Total files found: {len(files)}")
        return files
    
    def download_file(self, bucket, key, local_path):
        """
        下载单个文件
        
        Args:
            bucket (str): 存储桶名称，格式为 BucketName-APPID
            key (str): 对象键，即文件路径
            local_path (str): 本地保存路径
            
        Returns:
            bool: 下载是否成功
        """
        try:
            # 确保目标目录存在
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # 下载文件
            response = self.client.get_object(
                Bucket=bucket,
                Key=key
            )
            
            # 将文件内容写入本地文件
            response['Body'].get_stream_to_file(local_path)
            
            print(f"Successfully downloaded: {key} -> {local_path}")
            return True
            
        except Exception as e:
            print(f"Failed to download {key}: {str(e)}")
            return False
    
    def download_files(self, bucket, prefix, local_dir, file_pattern=None):
        """
        下载指定前缀下的所有文件
        
        Args:
            bucket (str): 存储桶名称，格式为 BucketName-APPID
            prefix (str): 要下载的目录前缀
            local_dir (str): 本地保存目录
            file_pattern (str, optional): 文件名匹配模式，如 "*.svg"
            
        Returns:
            dict: 下载统计信息
        """
        import fnmatch
        
        stats = {
            'total_files': 0,
            'successful': 0,
            'failed': 0,
            'failed_files': []
        }
        
        # 处理前缀中的通配符
        if '**' in prefix:
            # 移除**并获取基础前缀
            base_prefix = prefix.split('**')[0]
            print(f"Using base prefix: {base_prefix}")
            files = self.list_files(bucket, base_prefix, delimiter='')
        else:
            files = self.list_files(bucket, prefix, delimiter='/')
        
        # 确保本地目录存在
        os.makedirs(local_dir, exist_ok=True)
        
        # 下载文件
        for file_info in files:
            key = file_info['Key']
            
            # 如果指定了文件模式，检查是否匹配
            if file_pattern:
                basename = os.path.basename(key)
                if not fnmatch.fnmatch(basename, file_pattern):
                    continue
            
            # 如果指定了前缀模式，检查是否匹配完整路径
            if '**' in prefix:
                pattern = prefix.replace('**', '*')
                if not fnmatch.fnmatch(key, pattern):
                    continue
                
            stats['total_files'] += 1
            
            # 构建本地路径
            if prefix:
                rel_path = key
            else:
                rel_path = key
            local_path = os.path.join(local_dir, rel_path)
            
            # 下载文件
            if self.download_file(bucket, key, local_path):
                stats['successful'] += 1
            else:
                stats['failed'] += 1
                stats['failed_files'].append(key)
        
        # 打印统计信息
        print(f"\nDownload Summary:")
        print(f"Total files: {stats['total_files']}")
        print(f"Successfully downloaded: {stats['successful']}")
        print(f"Failed: {stats['failed']}")
        
        if stats['failed'] > 0:
            print("\nFailed files:")
            for file in stats['failed_files']:
                print(f"- {file}")
        
        return stats

def update_cos_files(local_files, cos_client, bucket, base_path=None, confirm=True):
    """更新COS中的文件

    Args:
        local_files (list): 本地文件路径列表
        cos_client: COS客户端实例
        bucket (str): 存储桶名称
        base_path (str): 基础路径，用于从本地路径中提取目标路径
        confirm (bool): 是否需要确认每个文件的更新

    Returns:
        tuple: (成功数量, 失败数量, 失败文件列表)
    """
    success_count = 0
    fail_count = 0
    failed_files = []

    # 展开基础路径中的波浪号
    if base_path:
        base_path = os.path.expanduser(base_path)

    # 处理所有文件模式
    for file_pattern in local_files:
        # 展开波浪号
        file_pattern = os.path.expanduser(file_pattern)
        
        # 使用glob展开文件模式
        matching_files = glob.glob(file_pattern)
        if not matching_files:
            print(f"警告: 没有找到匹配的文件: {file_pattern}")
            continue
            
        for local_path in matching_files:
            try:
                if base_path:
                    # 使用基础路径来构造目标路径
                    rel_path = os.path.relpath(local_path, base_path)
                    cos_key = rel_path  # 直接使用相对路径作为COS键
                else:
                    # 原有的路径处理逻辑
                    parts = local_path.split('story/posters/')
                    if len(parts) != 2:
                        print(f"无法解析文件路径: {local_path}")
                        fail_count += 1
                        failed_files.append(local_path)
                        continue
                    cos_key = f"story/posters/{parts[1]}"
                
                if confirm:
                    print("\n文件更新确认:")
                    print(f"本地文件: {local_path}")
                    print(f"COS目标: {cos_key}")
                    response = input("是否更新此文件? (y/n): ").lower()
                    if response != 'y':
                        print("已跳过此文件")
                        continue

                # 上传文件到COS
                with open(local_path, 'rb') as f:
                    cos_client.put_object(
                        Bucket=bucket,
                        Body=f,
                        Key=cos_key
                    )
                
                print(f"成功更新: {cos_key}")
                success_count += 1

            except Exception as e:
                print(f"更新失败 {local_path}: {str(e)}")
                fail_count += 1
                failed_files.append(local_path)

    return success_count, fail_count, failed_files

def get_cos_client():
    """
    获取COS客户端实例
    
    Returns:
        CosS3Client: COS客户端实例
    """
    # COS配置信息
    secret_id = os.environ.get('QCLOUD_SECRET_ID')
    secret_key = os.environ.get('QCLOUD_SECRET_KEY')
    region = os.environ.get('QCLOUD_REGION', 'ap-shanghai')
    
    if not secret_id or not secret_key:
        raise ValueError("请设置环境变量: QCLOUD_SECRET_ID 和 QCLOUD_SECRET_KEY")
    
    # 创建COS配置
    config = CosConfig(
        Region=region,
        SecretId=secret_id,
        SecretKey=secret_key
    )
    
    # 创建客户端实例
    return CosS3Client(config)

def get_bucket_name():
    """
    获取存储桶名称
    
    Returns:
        str: 存储桶名称
    """
    bucket = os.environ.get('QCLOUD_BUCKET')
    if not bucket:
        raise ValueError("请设置环境变量: QCLOUD_BUCKET")
    return bucket

def main():
    parser = argparse.ArgumentParser(
        description='腾讯云COS文件操作工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 下载指定前缀下的所有文件:
  python cos_downloader.py download "story/posters/"
  
  # 下载特定目录下的SVG文件:
  python cos_downloader.py download "story/posters/" -p "*.svg" -o ~/Downloads
  
  # 递归下载所有子目录中的特定文件:
  python cos_downloader.py download "story/posters/**/poster*.svg" -o ~/Downloads
  
  # 更新单个文件到COS:
  python cos_downloader.py update ~/Downloads/story/posters/123/cover.svg -b ~/Downloads
  
  # 批量更新文件到COS（带确认）:
  python cos_downloader.py update ~/Downloads/story/posters/*/cover*.svg -b ~/Downloads
  
  # 批量更新文件到COS（自动确认）:
  python cos_downloader.py update -y -b ~/Downloads ~/Downloads/story/posters/*/cover*.svg

注意:
  - 使用引号包裹带有通配符的路径以防止shell展开
  - 更新命令需要使用-b/--base指定基础路径以正确构造目标路径
  - 文件模式支持标准的通配符（*, ?, [seq], [!seq]）
"""
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 添加下载命令
    download_parser = subparsers.add_parser('download', help='从COS下载文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='从腾讯云COS下载文件到本地',
        epilog="""
示例:
  # 下载所有文件:
  python cos_downloader.py download "story/posters/"
  
  # 下载SVG文件:
  python cos_downloader.py download "story/posters/" -p "*.svg" -o ~/Downloads
  
  # 递归下载:
  python cos_downloader.py download "story/posters/**/poster*.svg" -o ~/Downloads
""")
    download_parser.add_argument('prefix', help='文件前缀路径，如 "story/posters/"')
    download_parser.add_argument('-p', '--pattern', help='文件名匹配模式，如 "*.svg"')
    download_parser.add_argument('-o', '--output', help='输出目录')
    
    # 添加更新命令
    update_parser = subparsers.add_parser('update', help='更新COS中的文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='将本地文件更新到腾讯云COS',
        epilog="""
示例:
  # 更新单个文件:
  python cos_downloader.py update ~/Downloads/story/posters/123/cover.svg -b ~/Downloads
  
  # 批量更新（带确认）:
  python cos_downloader.py update ~/Downloads/story/posters/*/cover*.svg -b ~/Downloads
  
  # 批量更新（自动确认）:
  python cos_downloader.py update -y -b ~/Downloads ~/Downloads/story/posters/*/cover*.svg
""")
    update_parser.add_argument('files', nargs='+', help='要更新的本地文件路径')
    update_parser.add_argument('-b', '--base', help='基础路径，用于构造目标路径')
    update_parser.add_argument('-y', '--yes', action='store_true', 
                             help='自动确认所有更新，不进行单个确认')

    args = parser.parse_args()

    try:
        # 初始化COS客户端
        cos_client = get_cos_client()
        bucket = get_bucket_name()

        if args.command == 'download':
            downloader = COSDownloader(cos_client)
            if args.output:
                os.makedirs(args.output, exist_ok=True)
            downloader.download_files(
                bucket, 
                args.prefix, 
                args.output or '.',
                file_pattern=args.pattern
            )
            
        elif args.command == 'update':
            print(f"准备更新 {len(args.files)} 个文件到COS...")
            success, fail, failed_files = update_cos_files(
                args.files, 
                cos_client, 
                bucket,
                base_path=args.base,
                confirm=not args.yes
            )
            
            print("\n更新完成:")
            print(f"成功: {success}")
            print(f"失败: {fail}")
            
            if failed_files:
                print("\n失败的文件:")
                for f in failed_files:
                    print(f"- {f}")
    
    except ValueError as e:
        print(f"错误: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"未知错误: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 