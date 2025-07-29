import os
from abc import ABC
from typing import Optional

from pydantic import Field
from pydantic_settings import SettingsConfigDict, BaseSettings

from feng_tools.app.config.AppInfoSetting import AppInfoSetting
from feng_tools.app.config.AppPathSetting import AAppPath
from feng_tools.app.config.DatabaseSetting import DatabaseSetting


class SettingsAppPath(AAppPath, ABC):
    @classmethod
    def get_env_file(cls) -> str:
        return os.path.join(cls.get_app_base_path(), ".env")

    @classmethod
    def get_app_settings_class(cls):
        AppPathSetting = cls.get_app_path_setting_class()


        # 使用新的元类创建AppSettings类
        class AppSettings(BaseSettings):
            """应用配置"""
            app_info:AppInfoSetting = Field(AppInfoSetting(), title='应用信息设置')
            app_path:AppPathSetting = Field(AppPathSetting(), title='应用路径设置')
            db:DatabaseSetting = Field(DatabaseSetting(), title='应用路径设置')

            model_config = SettingsConfigDict(
                env_file=cls.get_env_file(),
                env_file_encoding='utf-8',
                env_nested_delimiter='.',  # 指定嵌套键名的分隔符
                # 其他配置...
            )

            @property
            def root_path(self):
                return cls.get_root_path()


        return AppSettings


if __name__ == '__main__':
    from pathlib import Path
    class CustomSettingsAppPath(SettingsAppPath):
        @classmethod
        def get_root_path(cls):
            return Path(__file__).parent

        @classmethod
        def get_env_file(cls) -> str:
            return os.path.join(cls.get_root_path(), "demo.env")
    settings = CustomSettingsAppPath.get_app_settings_class()()
    print(settings.root_path)