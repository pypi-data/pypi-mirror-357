import os
from abc import ABC
from typing import Optional

from pydantic import Field
from pydantic_settings import SettingsConfigDict, BaseSettings

from feng_tools.app.config.AppInfoSetting import AppInfoSetting
from feng_tools.app.config.AppPathSetting import AAppPath
from feng_tools.app.config.DatabaseSetting import DatabaseSetting


class SettingsAppPath(AAppPath, ABC):
    """
    应用设置路径基类
    
    提供了一套灵活的环境配置文件管理机制，支持根据不同环境加载不同的配置文件。
    
    环境配置文件加载规则：
    1. 默认从环境变量ENV或ENVIRONMENT获取当前环境名称
    2. 根据环境名称查找对应的.env.{environment}文件
    3. 如果找不到特定环境的配置文件，则回退到默认的.env文件
    
    使用方法：
    1. 继承此类并实现必要的抽象方法
    2. 可选地重写get_environment和get_env_file方法以自定义环境检测和配置文件路径
    3. 调用get_app_settings_class()获取配置类
    4. 实例化配置类以获取应用配置
    
    示例见文件末尾的__main__部分
    """

    
    @classmethod
    def get_env_file(cls) -> str:
        """
        根据当前环境获取对应的.env文件路径
        环境配置文件命名规则：.env.dev.{environment}，如.env.dev, .env.dev.prod
        如果指定环境的配置文件不存在，则回退到默认的.env文件
        """
        env = cls.get_environment()
        base_path = cls.get_app_base_path()
        
        # 特定环境的配置文件路径
        env_specific_file = os.path.join(base_path, f".env.{env}")
        
        # 默认配置文件路径
        default_env_file = os.path.join(base_path, ".env")
        
        # 如果特定环境的配置文件存在，则使用它，否则使用默认配置文件
        if os.path.exists(env_specific_file):
            return env_specific_file
        return default_env_file

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
                # 配置文件设置
                env_file=cls.get_env_file(),
                env_file_encoding='utf-8',
                env_nested_delimiter='.',  # 指定嵌套键名的分隔符
                case_sensitive=False,  # 不区分大小写
                extra='ignore'  # 忽略未定义的配置项
            )

            @property
            def environment(self) -> str:
                """获取当前运行环境"""
                return cls.get_environment()

            @property
            def root_path(self):
                return cls.get_root_path()


        return AppSettings


if __name__ == '__main__':
    from pathlib import Path


    class CustomSettingsAppPath(SettingsAppPath):
        """
        自定义设置路径示例
        演示如何扩展SettingsAppPath类来自定义配置文件路径和环境检测
        """

        @classmethod
        def get_root_path(cls):
            return Path(__file__).parent.parent.parent.parent

        @classmethod
        def get_app_base_path(cls):
            return  Path(__file__).parent

    os.environ['ENV'] = 'prod'
    # 创建自定义设置类并实例化
    CustomSettings = CustomSettingsAppPath.get_app_settings_class()
    settings = CustomSettings()

    # 输出信息
    print(f"当前环境: {settings.environment}")
    print(f"根路径: {settings.root_path}")
    print(f"配置文件: {CustomSettingsAppPath.get_env_file()}")
    print(settings)