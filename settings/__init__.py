#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
设置模块初始化
存储和管理应用配置
"""

import os
import json

# 默认配置
DEFAULT_API_CONFIG = {
    'api_type': 'None',
    'api_key': None,
    'api_endpoint': None,
    'custom_params': {}
}

# 配置文件路径
API_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api_config.json')

def get_default_api_config():
    """返回默认API配置"""
    return DEFAULT_API_CONFIG.copy()
