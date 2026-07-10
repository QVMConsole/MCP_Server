"""QVMConsole MCP Server - 配置管理模块"""

import json
import os
from pathlib import Path
from typing import Optional


class Config:
    """配置管理类"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置

        Args:
            config_path: 配置文件路径，默认为 config/config.json
        """
        if config_path is None:
            # 默认配置文件路径
            config_path = os.getenv("CONFIG_PATH", "config/config.json")

        # 如果是相对路径，相对于当前文件所在目录的上级目录（项目根目录）
        if not os.path.isabs(config_path):
            # 获取当前文件所在目录的上级目录（项目根目录）
            project_root = Path(__file__).parent.parent
            config_path = project_root / config_path

        self.config_path = Path(config_path)
        self._load_config()

    def _load_config(self):
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"配置文件不存在: {self.config_path}\n"
                f"请复制 config/config.example.json 为 config/config.json 并填写正确的配置"
            )

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        # QVMConsole 配置
        qvm_config = config_data.get("qvmconsole", {})
        self.base_url = qvm_config.get("base_url", "http://localhost:8082").rstrip('/')
        self.api_key_id = qvm_config.get("api_key_id", "")
        self.api_key = qvm_config.get("api_key", "")
        self.timeout = qvm_config.get("timeout", 30)
        self.verify_ssl = qvm_config.get("verify_ssl", True)

        # MCP 配置
        mcp_config = config_data.get("mcp", {})
        self.server_name = mcp_config.get("server_name", "qvmconsole-mcp-server")
        self.version = mcp_config.get("version", "0.1.0")

        # 日志配置
        log_config = config_data.get("logging", {})
        self.log_level = log_config.get("level", "INFO")
        self.log_file = log_config.get("file", "logs/mcp-server.log")

        # 验证必需配置
        if not self.api_key_id or not self.api_key:
            raise ValueError(
                "API Key 配置缺失，请在配置文件中设置 api_key_id 和 api_key"
            )

    def get_auth_headers(self) -> dict:
        """
        获取认证请求头

        Returns:
            包含 API Key 认证信息的请求头字典
        """
        return {
            "X-API-Key-ID": self.api_key_id,
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }


# 全局配置实例
config: Optional[Config] = None


def init_config(config_path: Optional[str] = None) -> Config:
    """
    初始化全局配置

    Args:
        config_path: 配置文件路径

    Returns:
        配置实例
    """
    global config
    config = Config(config_path)
    return config


def get_config() -> Config:
    """
    获取全局配置实例

    Returns:
        配置实例

    Raises:
        RuntimeError: 如果配置未初始化
    """
    if config is None:
        raise RuntimeError("配置未初始化，请先调用 init_config()")
    return config
