from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos import CosServiceError
from qcloud_cos import CosClientError

import os
import hashlib

from ..utils.constants import (
    info_print, warn_print, error_print, debug_print
)

class CosUploader:
    def __init__(
        self,
        service_root,
        cos_region,
        cos_secret_id,
        cos_secret_key,
        cos_bucket,
        cos_token=None,
        cos_scheme="https",
    ):
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

    def calculate_file_hash(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def get_file_name(self, file_path, applyHash=True):
        filename, file_extension = os.path.splitext(os.path.basename(file_path))
        if file_extension in [".svg", ".jpg", ".jpeg", ".png", ".gif", ".bmp"]:
            return filename + (("_" + self.calculate_file_hash(file_path)) if applyHash else "") + file_extension
        else:
            return os.path.basename(file_path)

    def local2cos(self, local_path, story_id, target_relative_path="test", applyHash=True):
        if target_relative_path is None:
            target_relative_path = ""
        elif len(target_relative_path) > 0:
            target_relative_path = (
                target_relative_path
                if target_relative_path[0] != "/"
                else target_relative_path[1:]
            )
        try:
            filename = os.path.join(
                target_relative_path,
                story_id,
                self.get_file_name(local_path, applyHash=applyHash),
            )
        except:
            error_print(f"local2cos:", "file not found:", local_path)
            return None
        
        debug_print(f"local2cos - filename: {filename}", f"local_path: {local_path}", f"target_relative_path: {target_relative_path}", f"story_id: {story_id}")
        response = self._client.upload_file(
            Bucket=self._bucket, LocalFilePath=local_path, Key=filename
        )
        debug_print(f"response:", response)
        return "/"+filename
    
    def test2product(self, source):
        source_file = source[1:] if source.startswith("/") else source
        target_file = source_file
        if source_file.startswith("test/audios/") or source_file.startswith("test/posters/"):
            target_file = "story/" + source_file[len("test/"):]
        if source_file != target_file:
            info_print(f"test2product:", "copy from", source_file, "to", target_file)
            try:
                response = self._client.copy_object(
                    Bucket=self._bucket,
                    Key=target_file,
                    CopySource={
                        'Bucket': self._bucket, 
                        'Key': source_file, 
                        'Region': self._region
                    }
                )
            except Exception as e:
                error_print(f"test2product:", "copy test file to product path failed:", e)
        return "/"+target_file

    def copy2dest(self, source, dest):
        try:
            self._client.copy(
                Bucket=self._bucket,
                Key=dest,
                CopySource={
                    'Bucket': self._bucket, 
                    'Key': source, 
                    'Region': self._region
                }
            )
            info_print(f"copy2dest:", "file copied from", source, "to", dest)
        except Exception as e:
            error_print(f"copy2dest:", "Exception occured in copy2dest():\n", e)
            return source
        return dest
