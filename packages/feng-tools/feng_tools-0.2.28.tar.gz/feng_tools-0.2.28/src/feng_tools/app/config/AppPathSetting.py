import os
from abc import ABC
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings

from feng_tools.app.base.AppPath import AppPath


class AAppPath(AppPath, ABC):

    @classmethod
    def get_app_path_setting_class(cls):
        class AppPathSetting(BaseSettings):
            """应用配置"""
            # 数据存储路径
            data_dir: Optional[str] = Field(os.path.join(cls.get_root_path(), '.data'), title='数据存储路径')
            # 上传路径
            upload_dir: Optional[str] = Field(os.path.join(cls.get_root_path(), '.data', 'upload'), title='上传路径')
            # 日志存储路径
            log_dir: Optional[str] = Field(os.path.join(cls.get_root_path(), '.log'), title='日志存储路径')
            # 临时存储路径
            temp_dir: Optional[str] = Field(os.path.join(cls.get_root_path(), '.temp'), title='临时存储路径')
            # 静态资源路径
            static_dir: Optional[str] = Field(os.path.join(cls.get_root_path(), 'resource', 'static'), title='静态资源路径')
            # 模板文件路径
            templates_dir: Optional[str] = Field(os.path.join(cls.get_root_path(), 'resource', 'templates'), title='模板文件路径')
        return AppPathSetting