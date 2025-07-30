import hashlib
import io
import warnings
import subprocess
try:
    import pytest
except ImportError:
    warnings.warn("pip install pytest")
from kitx.lib_file_storage import FileStorageConfig, get_interface_client, FileStorageType


class TestMinio:

    @pytest.fixture(autouse=True)
    def init(self):
        self.client = get_interface_client(FileStorageConfig(
            fs_type=FileStorageType.Minio.value,
            fs_endpoint="127.0.0.1:9000",
            fs_secret_id="minioadmin",
            fs_secret_key="minioadmin",
            fs_bucket="paper",
            fs_region="ap-guangzhou",
        ))

    def test_run_docker_minio(self):
        bash = """docker run -d --name minio --rm
        -p 9000:9000 
        -p 9001:9001
        -e "MINIO_ROOT_USER=minioadmin"
        -e "MINIO_ROOT_PASSWORD=minioadmin"
        minio/minio:RELEASE.2025-05-24T17-08-30Z
        server /data --console-address :9001"
        """
        bash_list = [i for i in bash.replace("\n", "").split(" ") if i != ""]
        res = " ".join(bash_list)
        print(res)
        res = subprocess.run(res, shell=True, check=True, text=True)
        print(res.stdout)

    def test_upload(self):
        upload_bytes = b"hello"
        upload_io = io.BytesIO(upload_bytes)
        res = self.client.upload("hhh2.txt",
                                 upload_io,
                                 content_type="text/plain",
                                 metadata={"test_meta_key": "test_meta_value"}
                                 )
        print("etag", res)
        assert hashlib.md5(upload_bytes).hexdigest() == res

    def test_download(self):
        res = self.client.download("hhh2.txt")
        print("res", res)
