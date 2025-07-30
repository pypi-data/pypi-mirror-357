import io
import warnings
import hashlib
try:
    import pytest
except ImportError:
    warnings.warn("pip install pytest")
from kitx.lib_file_storage import FileStorageConfig, get_interface_client, FileStorageType


class TestCos:

    @pytest.fixture(autouse=True)
    def init(self):
        self.client = get_interface_client(FileStorageConfig(
            fs_type=FileStorageType.COS.value,
            fs_endpoint="cos.ap-guangzhou.myqcloud.com",
            fs_secret_id="AKIDwnSxEH3YnQs4ze3B5lCNJzQbZP3TeaHj",
            fs_secret_key="sY0HJ6jBOM7g2DDyWu51h8JEuKVxDF2a",
            fs_bucket="product-algo-paper-1358126726",
            fs_region="ap-guangzhou",
        ))
        self.upload_bytes = b"hello World"

    def test_upload(self):
        print('test_upload....')
        etag = self.client.upload("hhh1.txt", io.BytesIO(self.upload_bytes))
        etag = etag.replace('"', "")
        assert etag == hashlib.md5(self.upload_bytes).hexdigest()

    def test_download(self):
        print('test_download....')
        res = self.client.download("hhh1.txt")
        print("res", res)
        assert res == self.upload_bytes