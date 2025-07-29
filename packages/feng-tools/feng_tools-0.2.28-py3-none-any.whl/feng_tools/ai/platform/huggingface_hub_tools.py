"""
pip install huggingface_hub
"""
import os
from huggingface_hub import snapshot_download, login


class HuggingFaceHubTools:
    """Hugging Face Hub 工具类，用于模型下载和管理"""

    def __init__(self, cache_dir="./models", token=None):
        """
        初始化 Hugging Face Hub 工具类

        Args:
            cache_dir: 模型缓存目录
            token: Hugging Face API 令牌
        """
        # 设置超时时间（秒）
        os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "600"  # 设置为10分钟
        self.cache_dir = cache_dir
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
        self.token = token

        # 如果提供了令牌，登录到 Hugging Face Hub
        if token:
            login(token=token)

        # 确保缓存目录存在
        os.makedirs(cache_dir, exist_ok=True)

    def download_model(self, model_id):
        """
        从 Hugging Face Hub 下载模型
        Args:
            model_id: 模型 ID
        Returns:
            下载的模型本地路径
        """
        print(f"正在下载模型: {model_id}")
        model_path = snapshot_download(
            repo_id=model_id,
            local_dir=self.cache_dir,
            token=self.token
        )
        print(f"模型已下载到: {model_path}")
        return model_path

    def get_model_path(self, model_id):
        """
        获取模型的本地路径，如果模型不存在则下载
        Args:
            model_id: 模型 ID
        Returns:
            模型的本地路径
        """
        model_path = os.path.join(self.cache_dir, model_id.split('/')[-1])
        if not os.path.exists(model_path):
            return self.download_model(model_id)
        return model_path


if __name__ == '__main__':
    model_id = "stable-diffusion-v1-5/stable-diffusion-v1-5"
    tool = HuggingFaceHubTools(cache_dir=rf'D:\models\ai_models\{model_id}', token='xxx')
    tool.download_model(model_id)
    pass
