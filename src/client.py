"""QVMConsole API 客户端封装"""

import httpx
from typing import Optional, Dict, Any, List
from loguru import logger


class QVMConsoleAPIError(Exception):
    """QVMConsole API 错误"""
    def __init__(self, message: str, status_code: int = 0, response_data: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class QVMConsoleClient:
    """QVMConsole API 客户端类"""
    
    def __init__(self, config):
        """
        初始化客户端
        
        Args:
            config: 配置对象
        """
        self.base_url = config.qvmconsole["base_url"].rstrip('/')
        self.api_key_id = config.qvmconsole["api_key_id"]
        self.api_key = config.qvmconsole["api_key"]
        self.timeout = config.qvmconsole["timeout"]
        self.verify_ssl = config.qvmconsole["verify_ssl"]
        self.headers = {
            "X-API-Key-ID": self.api_key_id,
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # 验证必需配置
        if not self.base_url or not self.api_key_id or not self.api_key:
            raise ValueError(
                "QVMConsole 配置缺失！\n"
                "请通过以下方式之一提供配置：\n"
                "1. 环境变量: QVMC_BASE_URL, QVMC_API_KEY_ID, QVMC_API_KEY\n"
                "2. 配置文件: config/config.json\n"
                "3. Claude Desktop 配置中的 env 字段"
            )
        
        logger.info(f"🔗 连接到 QVMConsole: {self.base_url}")

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
        获取虚拟机可用的存储位置列表

        Returns:
            存储位置列表,每个存储位置包含 ID、名称、可用空间等信息
        """
        data = await self._request("GET", "/api/storage-pool/vm-targets")
        return data if isinstance(data, list) else []

    async def list_switches(self) -> Dict[str, Any]:
        """
        获取 VPC 交换机列表

        Returns:
            交换机列表数据
        """
        return await self._request("GET", "/api/vpc/switches")

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
                - nic_model: 网卡模型 (可选，virtio/e1000e/rtl8139)
                - switch_id: VPC 交换机 ID (可选)
                - security_group_id: 安全组 ID (可选)

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
                - add_disks: 新增磁盘列表 (可选)

        Returns:
            修改结果
        """
        return await self._request("PUT", f"/api/vm/{vm_name}", json_data=params)

    async def add_disk(self, vm_name: str, size_gb: int, format: str = "qcow2", bus: str = "virtio") -> Dict[str, Any]:
        """
        为虚拟机添加新硬盘

        Args:
            vm_name: 虚拟机名称
            size_gb: 磁盘大小（GB）
            format: 磁盘格式（qcow2/raw，默认 qcow2）
            bus: 磁盘总线（virtio/scsi/sata/ide，默认 virtio）

        Returns:
            添加结果
        """
        params = {
            "size_gb": size_gb,
            "format": format,
            "bus": bus
        }
        return await self._request("POST", f"/api/vm/{vm_name}/disk", json_data=params)

    async def list_disks(self, vm_name: str) -> List[Dict[str, Any]]:
        """
        获取虚拟机磁盘列表

        Args:
            vm_name: 虚拟机名称

        Returns:
            磁盘列表
        """
        data = await self._request("GET", f"/api/vm/{vm_name}/disks")
        return data if isinstance(data, list) else []

    async def resize_disk(self, vm_name: str, dev: str, size_gb: int) -> Dict[str, Any]:
        """
        扩容虚拟机磁盘

        Args:
            vm_name: 虚拟机名称
            dev: 设备名称（如 vda, vdb）
            size_gb: 新的大小（GB，必须大于当前大小）

        Returns:
            扩容结果
        """
        params = {"size_gb": size_gb}
        return await self._request("POST", f"/api/vm/{vm_name}/disk/{dev}/resize", json_data=params)

    async def reset_vm_password(self, vm_name: str, username: str, password: str) -> Dict[str, Any]:
        """
        重置虚拟机用户密码

        Args:
            vm_name: 虚拟机名称
            username: 用户名
            password: 新密码

        Returns:
            重置结果，包含 task_id
        """
        params = {
            "username": username,
            "password": password
        }
        return await self._request("POST", f"/api/vm/{vm_name}/password/reset", json_data=params)

    async def get_task_detail(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务详情

        Args:
            task_id: 任务 ID

        Returns:
            任务详情
        """
        return await self._request("GET", f"/api/task/{task_id}")

    async def vm_power_operation(self, vm_name: str, action: str) -> Dict[str, Any]:
        """
        虚拟机电源操作

        Args:
            vm_name: 虚拟机名称
            action: 操作类型 (start/shutdown/destroy/reboot/reset)

        Returns:
            操作结果
        """
        return await self._request("POST", f"/api/vm/{vm_name}/operate", json_data={"action": action})

    async def list_snapshots(self, vm_name: str) -> Dict[str, Any]:
        """
        获取虚拟机快照列表

        Args:
            vm_name: 虚拟机名称

        Returns:
            快照列表数据（包含 data 和 quota 信息）
        """
        return await self._request("GET", f"/api/vm/{vm_name}/snapshots")

    async def create_snapshot(self, vm_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建虚拟机快照

        Args:
            vm_name: 虚拟机名称
            params: 快照参数，包含:
                - name: 快照名称 (必填)
                - description: 快照描述 (可选)
                - include_memory: 是否包含内存状态 (可选，默认 false)
                - auto_fix_nvram: 自动修复 NVRAM (可选，默认 false)

        Returns:
            创建结果，包含 task_id
        """
        return await self._request("POST", f"/api/vm/{vm_name}/snapshot", json_data=params)

    async def revert_snapshot(self, vm_name: str, snap_name: str) -> Dict[str, Any]:
        """
        恢复虚拟机快照

        Args:
            vm_name: 虚拟机名称
            snap_name: 快照名称

        Returns:
            恢复结果，包含 task_id
        """
        return await self._request("POST", f"/api/vm/{vm_name}/snapshot/{snap_name}/revert")

    async def delete_snapshot(self, vm_name: str, snap_name: str) -> Dict[str, Any]:
        """
        删除虚拟机快照

        Args:
            vm_name: 虚拟机名称
            snap_name: 快照名称

        Returns:
            删除结果，包含 task_id
        """
        return await self._request("DELETE", f"/api/vm/{vm_name}/snapshot/{snap_name}")

    async def list_vm_schedules(self, vm_name: str) -> List[Dict[str, Any]]:
        """
        获取虚拟机定时任务列表

        Args:
            vm_name: 虚拟机名称

        Returns:
            定时任务列表
        """
        data = await self._request("GET", f"/api/vm/{vm_name}/schedules")
        return data if isinstance(data, list) else []

    async def create_vm_schedule(self, vm_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建虚拟机定时任务

        Args:
            vm_name: 虚拟机名称
            params: 定时任务参数，包含:
                - event_type: 事件类型 (power/vm)
                - action: 操作类型 (start/shutdown/delete)
                - schedule_type: 计划类型 (once/daily/weekly)
                - run_at: 执行时间 (once 类型使用，格式: 2024-01-01 10:00:00)
                - time_of_day: 每日执行时间 (daily/weekly 类型使用，格式: 14:30)
                - weekdays: 星期几执行 (weekly 类型使用，1-7 表示周一到周日)
                - timezone: 时区 (可选，默认 Asia/Shanghai)
                - enabled: 是否启用 (可选，默认 true)

        Returns:
            创建结果
        """
        return await self._request("POST", f"/api/vm/{vm_name}/schedules", json_data=params)

    async def delete_vm_schedule(self, vm_name: str, schedule_id: int) -> Dict[str, Any]:
        """
        删除虚拟机定时任务

        Args:
            vm_name: 虚拟机名称
            schedule_id: 定时任务 ID

        Returns:
            删除结果
        """
        return await self._request("DELETE", f"/api/vm/{vm_name}/schedules/{schedule_id}")

    async def get_vm_stats(self, vm_name: str) -> Dict[str, Any]:
        """
        获取虚拟机实时监控数据

        Args:
            vm_name: 虚拟机名称

        Returns:
            监控数据（CPU、内存、磁盘、网络等）
        """
        return await self._request("GET", f"/api/vm/{vm_name}/stats")

    async def get_vm_stats_history(self, vm_name: str, hours: int = 24) -> Dict[str, Any]:
        """
        获取虚拟机历史监控数据

        Args:
            vm_name: 虚拟机名称
            hours: 查询小时数（默认 24 小时）

        Returns:
            历史监控数据
        """
        return await self._request("GET", f"/api/vm/{vm_name}/stats/history", params={"hours": hours})

    async def get_vnc_status(self, vm_name: str) -> Dict[str, Any]:
        """
        获取虚拟机 VNC 状态

        Args:
            vm_name: 虚拟机名称

        Returns:
            VNC 状态信息（enabled, port, auth, password, exposed 等）
        """
        return await self._request("GET", f"/api/vm/{vm_name}/vnc/status")

    async def enable_vnc(self, vm_name: str, password: Optional[str] = None) -> Dict[str, Any]:
        """
        开启虚拟机 VNC

        Args:
            vm_name: 虚拟机名称
            password: VNC 密码（可选，不填则无密码）

        Returns:
            操作结果
        """
        json_data = {"password": password} if password else {}
        return await self._request("POST", f"/api/vm/{vm_name}/vnc/enable", json_data=json_data)

    async def expose_vnc(self, vm_name: str, expose: bool) -> Dict[str, Any]:
        """
        切换 VNC 对外暴露状态

        Args:
            vm_name: 虚拟机名称
            expose: True=对外暴露(0.0.0.0)，False=仅本地(127.0.0.1)

        Returns:
            操作结果
        """
        json_data = {"expose": expose}
        return await self._request("POST", f"/api/vm/{vm_name}/vnc/expose", json_data=json_data)
