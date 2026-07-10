"""QVMConsole API 客户端封装"""

import httpx
from typing import Optional, Dict, Any, List
from loguru import logger

try:
    from .config import get_config
except ImportError:
    from config import get_config


class QVMConsoleAPIError(Exception):
    """QVMConsole API 错误"""
    def __init__(self, message: str, status_code: int = 0, response_data: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class QVMConsoleClient:
    """QVMConsole API 客户端"""

    def __init__(self):
        """初始化客户端"""
        self.config = get_config()
        self.base_url = self.config.base_url
        self.headers = self.config.get_auth_headers()
        self.timeout = self.config.timeout
        self.verify_ssl = self.config.verify_ssl

    async def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        发送 HTTP 请求

        Args:
            method: HTTP 方法 (GET, POST, PUT, DELETE)
            endpoint: API 端点路径（不包含 base_url）
            json_data: JSON 请求体
            params: URL 查询参数

        Returns:
            API 响应的 data 字段内容

        Raises:
            QVMConsoleAPIError: API 请求失败
        """
        url = f"{self.base_url}{endpoint}"

        logger.debug(f"发送请求: {method} {url}")
        if json_data:
            logger.debug(f"请求数据: {json_data}")

        try:
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=json_data,
                    params=params
                )

                # 解析响应
                try:
                    result = response.json()
                except Exception:
                    raise QVMConsoleAPIError(
                        f"API 响应解析失败: {response.text[:200]}",
                        status_code=response.status_code
                    )

                # 检查响应状态
                code = result.get("code", 0)
                message = result.get("message", "未知错误")

                if code != 200:
                    logger.error(f"API 错误: {code} - {message}")
                    raise QVMConsoleAPIError(
                        message=message,
                        status_code=code,
                        response_data=result
                    )

                logger.debug(f"请求成功: {message}")
                return result.get("data", {})

        except httpx.TimeoutException:
            raise QVMConsoleAPIError(f"请求超时: {url}")
        except httpx.RequestError as e:
            raise QVMConsoleAPIError(f"网络请求失败: {str(e)}")

    async def list_templates(self) -> List[Dict[str, Any]]:
        """
        获取模板列表

        Returns:
            模板列表，每个模板包含名称、显示名称、类型等信息
        """
        data = await self._request("GET", "/api/template/list")
        return data if isinstance(data, list) else []

    async def list_storage_pools(self) -> List[Dict[str, Any]]:
        """
        获取存储池列表

        Returns:
            存储池列表，每个存储池包含 ID、名称、可用空间等信息
        """
        data = await self._request("GET", "/api/storage-pool/list")
        return data if isinstance(data, list) else []

    async def create_vm_from_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        从模板创建虚拟机（克隆）

        Args:
            params: 创建参数，包含:
                - template: 模板名称 (必填)
                - name: 虚拟机名称 (必填)
                - vcpu: CPU 核心数 (必填)
                - ram: 内存大小 GB (必填)
                - disk_size: 磁盘大小 GB (可选)
                - hostname: 主机名 (可选)
                - password: 登录密码 (可选)
                - user: 用户名 (可选)
                - autostart: 是否自动启动 (可选)
                - remark: 备注 (可选)
                - storage_pool_id: 存储池 ID (可选，不指定则使用默认存储池)

        Returns:
            创建结果，包含 task_id
        """
        return await self._request("POST", "/api/vm/clone", json_data=params)

    async def get_vm_info(self, vm_name: str) -> Dict[str, Any]:
        """
        获取虚拟机详细信息

        Args:
            vm_name: 虚拟机名称

        Returns:
            虚拟机详细信息，包括密码
        """
        return await self._request("GET", f"/api/vm/{vm_name}")

    async def list_vms(self) -> List[Dict[str, Any]]:
        """
        列出所有虚拟机

        Returns:
            虚拟机列表
        """
        data = await self._request("GET", "/api/vm/list")
        return data if isinstance(data, list) else []

    async def edit_vm(self, vm_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        编辑虚拟机配置

        Args:
            vm_name: 虚拟机名称
            params: 修改参数，包含:
                - vcpu: CPU 核心数 (可选)
                - ram: 内存大小 GB (可选)
                - remark: 备注 (可选)
                - autostart: 自动启动 (可选)

        Returns:
            修改结果
        """
        return await self._request("PUT", f"/api/vm/{vm_name}", json_data=params)

    async def get_task_detail(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务详情

        Args:
            task_id: 任务 ID

        Returns:
            任务详情
        """
        return await self._request("GET", f"/api/task/{task_id}")
