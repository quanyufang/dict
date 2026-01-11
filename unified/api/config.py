#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件

支持从环境变量读取配置
"""

import os
from typing import Optional


class Config:
    """应用配置"""
    
    # 数据库配置
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "fishenglish_dict")
    DB_USER: str = os.getenv("DB_USER", "fishenglish")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "yu^&5432")
    
    # API配置
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # CORS配置
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    @classmethod
    def get_db_url(cls) -> str:
        """获取数据库连接URL"""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"


config = Config()

