"""配置管理模块"""

import os
import sys
import json
from pathlib import Path
from loguru import logger


class Config:
    """配置类"""
    
    def __init__(self):
        self.qvmconsole = {
            "base_url": "",
            "api_key_id": "",
            "api_key": "",
            "timeout": 30,
            "verify_ssl": True
        }
        self.logging = {
            "level": "INFO",
            "file": "logs/mcp-server.log"
        }


def init_config() -> Config:
    """
    初始化配置，优先级：
    1. 环境变量
    2. 配置文件 (config/config.json)
    3. 默认值
    """
    config = Config()
    
    # 1. 尝试从环境变量读取
    env_base_url = os.getenv("QVMC_BASE_URL")
    env_api_key_id = os.getenv("QVMC_API_KEY_ID")
    env_api_key = os.getenv("QVMC_API_KEY")
    
    if env_base_url and env_api_key_id and env_api_key:
        logger.info("✅ 从环境变量加载配置")
        config.qvmconsole["base_url"] = env_base_url
        config.qvmconsole["api_key_id"] = env_api_key_id
        config.qvmconsole["api_key"] = env_api_key
        
        # 可选的环境变量
        if os.getenv("QVMC_TIMEOUT"):
            config.qvmconsole["timeout"] = int(os.getenv("QVMC_TIMEOUT"))
        if os.getenv("QVMC_VERIFY_SSL"):
            config.qvmconsole["verify_ssl"] = os.getenv("QVMC_VERIFY_SSL").lower() == "true"
        
        return config
    
    # 2. 尝试从配置文件读取
    config_file = Path(__file__).parent.parent / "config" / "config.json"
    
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if "qvmconsole" in data:
                config.qvmconsole.update(data["qvmconsole"])
            
            if "logging" in data:
                config.logging.update(data["logging"])
            
            logger.info(f"✅ 从配置文件加载配置: {config_file}")
            return config
            
        except Exception as e:
            logger.warning(f"⚠️  读取配置文件失败: {e}")
    
    # 3. 检查是否有配置
    if not config.qvmconsole["base_url"]:
        logger.warning("⚠️  未找到配置文件，请通过环境变量或配置文件提供 QVMConsole 连接信息")
        logger.info("环境变量:")
        logger.info("  QVMC_BASE_URL        - QVMConsole 地址")
        logger.info("  QVMC_API_KEY_ID      - API Key ID")
        logger.info("  QVMC_API_KEY         - API Key")
        logger.info("  QVMC_TIMEOUT         - 超时时间（可选，默认 30）")
        logger.info("  QVMC_VERIFY_SSL      - 是否验证 SSL（可选，默认 true）")
        logger.info("")
        logger.info("或创建配置文件: config/config.json")
    
    return config
