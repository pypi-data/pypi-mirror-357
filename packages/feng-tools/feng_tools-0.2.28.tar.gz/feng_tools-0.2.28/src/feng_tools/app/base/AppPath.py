import os
from abc import ABC, abstractmethod


class AppPath(ABC):

    @classmethod
    @abstractmethod
    def get_root_path(cls):
        pass

    @classmethod
    def get_app_base_path(cls):
        return cls.get_root_path()

    @classmethod
    def get_environment(cls) -> str:
        """
        获取当前环境名称
        默认从环境变量ENV或ENVIRONMENT中获取，如果未设置则返回'dev'
        子类可以重写此方法以提供自定义的环境获取逻辑
        """
        env = os.environ.get('ENV') or os.environ.get('ENVIRONMENT') or 'dev'
        return env.lower()
