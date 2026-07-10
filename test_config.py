#!/usr/bin/env python3
"""
测试配置加载
用于验证环境变量配置是否正常工作
"""

import os
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import init_config
from loguru import logger

def test_config():
    """测试配置加载"""
    logger.info("开始测试配置...")
    
    # 初始化配置
    config = init_config()
    
    # 检查配置
    base_url = config.qvmconsole.get("base_url", "")
    api_key_id = config.qvmconsole.get("api_key_id", "")
    api_key = config.qvmconsole.get("api_key", "")
    
    if not base_url:
        logger.error("❌ 配置失败: 未找到 QVMC_BASE_URL")
        return False
    
    if not api_key_id:
        logger.error("❌ 配置失败: 未找到 QVMC_API_KEY_ID")
        return False
    
    if not api_key:
        logger.error("❌ 配置失败: 未找到 QVMC_API_KEY")
        return False
    
    logger.info(f"✅ 配置加载成功!")
    logger.info(f"   BASE_URL: {base_url}")
    logger.info(f"   API_KEY_ID: {api_key_id[:10]}...")
    logger.info(f"   API_KEY: {api_key[:10]}...")
    logger.info(f"   TIMEOUT: {config.qvmconsole.get('timeout', 30)}")
    logger.info(f"   VERIFY_SSL: {config.qvmconsole.get('verify_ssl', True)}")
    
    return True

if __name__ == "__main__":
    success = test_config()
    sys.exit(0 if success else 1)
