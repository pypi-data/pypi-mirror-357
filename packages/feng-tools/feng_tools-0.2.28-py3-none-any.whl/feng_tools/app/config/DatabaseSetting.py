import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSetting(BaseSettings):
    """数据库配置"""
    db_url:Optional[str] = Field(os.getenv("DB_URL", 'mysql+pymysql://root:123456@127.0.0.1:3306/test_db'), title='数据库连接url')
    db_async_url:Optional[str] = Field(os.getenv("DB_ASYNC_URL", 'mysql+aiomysql://root:123456@127.0.0.1:3306/test_db'), title='数据库连接异步url')
    host: Optional[str] = Field(os.getenv("DB_HOST", "127.0.0.1"), title='数据库主机')
    port: Optional[int] = Field(os.getenv("DB_PORT", 5432), title='数据库端口')
    name: Optional[str] = Field(os.getenv("DB_NAME", "test-db"), title='数据库名称')
    user: Optional[str] = Field(os.getenv("DB_USER", "root"), title='数据库用户名')
    password: Optional[str] = Field(os.getenv("DB_PASSWORD", "123456"), title='数据库密码')

    @property
    def url(self) -> str:
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def async_url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
