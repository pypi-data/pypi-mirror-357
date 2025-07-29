from abc import ABC, abstractmethod


class AppPath(ABC):

    @classmethod
    @abstractmethod
    def get_root_path(cls):
        pass

    @classmethod
    def get_app_base_path(cls):
        return cls.get_root_path()

