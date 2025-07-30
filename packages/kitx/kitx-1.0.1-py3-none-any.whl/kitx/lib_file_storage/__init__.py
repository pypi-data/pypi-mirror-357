from .func import FileStorageType, FileStorageConfig

"""
    枚举 和 配置
    配置 支持环境变量，且以 fastKit_fileStorage_    前缀开头
"""

from .func import get_interface_client

"""
    根据配置获取 实例
"""

from .func import object_upload, object_download

"""
    具体实现：
    example:
        config = FileStorageConfig(type=FileStorageType.COS,
                          endpoint"cos.ap-guangzhou.myqcloud.com",
                          secret_id="AKIDwnSxEH3YnQs4ze3B5lCNJzQbZP3TeaHj",
                          secret_key="sY0HJ6jBOM7g2DDyWu51h8JEuKVxDF2a",
        )
        
        c = get_interface_client(config)
   
        object_upload(c, "test.txt", io.Bytes(b"hello"))     
        
        or 
        
        c.upload("test.txt", bytes_io)
"""

__all__ = (
    "FileStorageType",
    "FileStorageConfig",

    "get_interface_client",

    "object_upload",
    "object_download"
)
