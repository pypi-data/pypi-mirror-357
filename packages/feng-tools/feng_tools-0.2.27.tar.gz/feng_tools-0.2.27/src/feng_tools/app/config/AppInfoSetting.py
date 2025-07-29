from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class AppInfoSetting(BaseSettings):
    # 应用标题
    title: Optional[str] = Field(None, title='应用标题')
    # 应用描述
    description: Optional[str] = Field(None, title='应用描述')
    # 应用编码
    code: Optional[str] = Field(None, title='应用编码')
    # 应用前缀
    prefix: Optional[str] = Field(None, title='应用路径前缀')
    # 应用端口（默认会使用总应用端口，如果和总应用端口不同，则会开启单独子应用）
    port: Optional[int] = Field(None, title='应用端口')