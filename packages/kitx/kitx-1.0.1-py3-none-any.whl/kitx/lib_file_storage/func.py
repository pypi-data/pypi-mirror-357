import io
from typing import Optional, ClassVar, Literal
from .interface import ObjectInterface
from pydantic_settings import BaseSettings, SettingsConfigDict

from enum import Enum

from kitx import env_prefix


class FileStorageType(Enum):
    OSS = "oss"
    Minio = "minio"
    COS = "cos"


class FileStorageConfig(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(env_prefix=env_prefix,
                                                                    use_enum_values=True)

    fs_type: FileStorageType = FileStorageType.COS.value
    # env["fastKit_fileStorage_endpoint"]
    fs_endpoint: str = "cos.ap-guangzhou.myqcloud.com"
    # env["fastKit_fileStorage_secret_id"]
    fs_secret_id: str = "AKIDwnSxEH3YnQs4ze3B5lCNJzQbZP3TeaHj"
    # env["fastKit_fileStorage_secret_key"]
    fs_secret_key: str = "sY0HJ6jBOM7g2DDyWu51h8JEuKVxDF2a"
    # bucket: str = "test-1358126726"
    # env["fastKit_fileStorage_bucket"]
    fs_bucket: str = "product-algo-paper-1358126726"
    # env["fastKit_fileStorage_scheme"]
    fs_scheme: str = "https"
    # env["fastKit_fileStorage_region"]
    fs_region: str = 'ap-guangzhou'
    fs_secure: bool = False


def get_interface_client(c: FileStorageConfig) -> ObjectInterface:
    if c.fs_type == FileStorageType.COS.value:
        from ._cos import CosImpl
        return CosImpl(c)

    elif c.fs_type == FileStorageType.Minio.value:
        from ._minio import MinioImpl
        return MinioImpl(c)

    elif c.fs_type == FileStorageType.OSS.value:
        from ._oss import OssImpl
        return OssImpl(c)
    else:
        raise TypeError(f"Unsupported file storage type: {c.type}")


def object_upload(obj: ObjectInterface,
                  file_path_name: str,
                  bytes_io: io.BytesIO,
                  length: Optional[int],
                  metadata=None,
                  **kwargs):
    return obj.upload(file_path_name, bytes_io, length, metadata, **kwargs)


def object_download(obj: ObjectInterface, file_path_name: str):
    return obj.download(file_path_name)
