"""
配置文件
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    
    # 智联招聘配置
    ZHILIAN_BASE_URL: str = "https://www.zhaopin.com"
    ZHILIAN_LOGIN_URL: str = "https://passport.zhaopin.com/login"
    ZHILIAN_SEARCH_URL: str = "https://www.zhaopin.com/sou"
    
    # 登录配置
    ZHILIAN_USERNAME: Optional[str] = None  # 手机号
    USERNAME: Optional[str] = None  # 兼容性保留，但优先使用ZHILIAN_USERNAME
    PASSWORD: Optional[str] = None  # 已废弃，保留兼容性
    LOGIN_TYPE: str = "sms"  # sms（短信验证码）或 qrcode（二维码扫码）
    
    # 浏览器配置
    HEADLESS: bool = False
    BROWSER_TIMEOUT: int = 30
    IMPLICIT_WAIT: int = 10
    
    # WebSocket配置
    WS_RECONNECT_INTERVAL: int = 5
    WS_MAX_RECONNECT_ATTEMPTS: int = 10
    
    # 中心服务器配置
    CENTER_SERVER_URL: Optional[str] = None
    CENTER_SERVER_TOKEN: Optional[str] = None
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "zhilian_bot.log"
    
    # 其他配置
    REQUEST_DELAY: float = 1.0  # 请求间隔（秒）
    MAX_RETRY_ATTEMPTS: int = 3
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()