"""MCP 工具定义"""

from typing import Any, Dict, List, Optional
from loguru import logger

try:
    from .client import QVMConsoleClient, QVMConsoleAPIError
except ImportError:
    from client import QVMConsoleClient, QVMConsoleAPIError


class QVMConsoleTools:
    """QVMConsole MCP 工具集"""

    def __init__(self):
        """初始化工具集"""
        self.client = QVMConsoleClient()

    async def list_templates(self) -> str:
        """
        列出所有可用的虚拟机模板

        Returns:
            格式化的模板列表字符串
        """
        try:
            templates = await self.client.list_templates()

            if not templates:
                return "当前没有可用的虚拟机模板"

            result = "可用的虚拟机模板列表:\n\n"
            for i, tpl in enumerate(templates, 1):
                name = tpl.get("name", "未知")
                display_name = tpl.get("display_name", name)
                tpl_type = tpl.get("type", "未知")
                category = tpl.get("category", "")
                disabled = tpl.get("disabled", False)

                status = "❌ 已禁用" if disabled else "✅ 可用"

                result += f"{i}. **{display_name}** ({name})\n"
                result += f"   - 类型: {tpl_type}\n"
                if category:
                    result += f"   - 分类: {category}\n"
                result += f"   - 状态: {status}\n\n"

            return result

        except QVMConsoleAPIError as e:
            logger.error(f"获取模板列表失败: {e}")
            return f"❌ 获取模板列表失败: {str(e)}"

    async def list_storage_pools(self) -> str:
        """
        列出所有存储池

        Returns:
            格式化的存储池列表字符串
        """
        try:
            pools = await self.client.list_storage_pools()

            if not pools:
                return "当前没有配置的存储池"

            result = "可用的存储池列表:\n\n"
            for i, pool in enumerate(pools, 1):
                pool_id = pool.get("id", "未知")
                display_name = pool.get("display_name", pool_id)
                enabled = pool.get("enabled", False)
                is_default = pool.get("is_default", False)
                can_use = pool.get("can_use_for_vm", False)
                
                # 获取空间信息
                total_gb = pool.get("total_gb", 0)
                available_gb = pool.get("available_gb", 0)
                used_percent = pool.get("used_percent", 0)

                # 状态图标
                status_icon = "✅" if (enabled and can_use) else "❌"
                default_text = " (默认)" if is_default else ""

                result += f"{i}. {status_icon} **{display_name}**{default_text}\n"
                result += f"   - ID: `{pool_id}`\n"
                result += f"   - 总容量: {total_gb:.1f} GB\n"
                result += f"   - 可用空间: {available_gb:.1f} GB\n"
                result += f"   - 使用率: {used_percent:.1f}%\n"
                result += f"   - 状态: {'已启用' if enabled else '已禁用'}\n"
                
                if not can_use:
                    reason = pool.get("status_reason", "不可用")
                    result += f"   - ⚠️ 提示: {reason}\n"
                
                result += "\n"

            return result

        except QVMConsoleAPIError as e:
            logger.error(f"获取存储池列表失败: {e}")
            return f"❌ 获取存储池列表失败: {str(e)}"

    async def create_vm_from_template(
        self,
        template_name: str,
        vm_name: str,
        vcpu: int,
        ram: int,
        disk_size: Optional[int] = None,
        hostname: Optional[str] = None,
        password: Optional[str] = None,
        user: Optional[str] = None,
        autostart: bool = False,
        remark: Optional[str] = None,
        storage_pool_id: Optional[str] = None
    ) -> str:
        """
        从模板创建虚拟机

        Args:
            template_name: 模板名称
            vm_name: 虚拟机名称
            vcpu: CPU 核心数
            ram: 内存大小（GB）
            disk_size: 磁盘大小（GB），不填则使用模板默认值
            hostname: 主机名，不填则使用虚拟机名称
            password: 登录密码，不填则自动生成
            user: 用户名，不填则使用模板默认用户
            autostart: 是否创建后自动启动
            remark: 备注信息
            storage_pool_id: 存储池 ID，不填则使用默认存储池

        Returns:
            创建结果信息
        """
        try:
            # 构建请求参数
            params = {
                "template": template_name,
                "name": vm_name,
                "vcpu": vcpu,
                "ram": ram,
                "autostart": autostart
            }

            if disk_size is not None:
                params["disk_size"] = disk_size
            if hostname:
                params["hostname"] = hostname
            if password:
                params["password"] = password
            if user:
                params["user"] = user
            if remark:
                params["remark"] = remark
            if storage_pool_id:
                params["storage_pool_id"] = storage_pool_id

            # 发送创建请求
            result = await self.client.create_vm_from_template(params)
            task_id = result.get("task_id", "")

            response = f"✅ 虚拟机创建任务已提交\n\n"
            response += f"- 虚拟机名称: {vm_name}\n"
            response += f"- 使用模板: {template_name}\n"
            response += f"- CPU: {vcpu} 核心\n"
            response += f"- 内存: {ram} GB\n"
            if disk_size:
                response += f"- 磁盘: {disk_size} GB\n"
            if storage_pool_id:
                response += f"- 存储池: {storage_pool_id}\n"
            if hostname:
                response += f"- 主机名: {hostname}\n"
            if autostart:
                response += f"- 自动启动: 是\n"
            response += f"\n任务 ID: {task_id}\n"
            response += f"\n提示: 使用 get_vm_info 查看虚拟机详情和密码"

            return response

        except QVMConsoleAPIError as e:
            logger.error(f"创建虚拟机失败: {e}")
            return f"❌ 创建虚拟机失败: {str(e)}"

    async def get_vm_info(self, vm_name: str, show_password: bool = True) -> str:
        """
        获取虚拟机详细信息

        Args:
            vm_name: 虚拟机名称
            show_password: 是否显示密码（默认显示）

        Returns:
            格式化的虚拟机信息
        """
        try:
            vm = await self.client.get_vm_info(vm_name)

            result = f"虚拟机详细信息: **{vm_name}**\n\n"

            # 基本信息
            result += "## 基本信息\n"
            result += f"- 名称: {vm.get('name', '未知')}\n"
            result += f"- 状态: {vm.get('status', '未知')}\n"
            result += f"- UUID: {vm.get('uuid', '未知')}\n"

            remark = vm.get('remark', '')
            if remark:
                result += f"- 备注: {remark}\n"

            # 硬件配置
            result += "\n## 硬件配置\n"
            result += f"- CPU: {vm.get('vcpu', 0)} 核心\n"
            result += f"- 内存: {vm.get('memory', 0)} MB\n"

            max_memory = vm.get('max_memory', 0)
            if max_memory > 0:
                result += f"- 最大内存: {max_memory} MB\n"

            # 网络信息
            result += "\n## 网络信息\n"
            ip_address = vm.get('ip', '')
            if ip_address:
                result += f"- IP 地址: {ip_address}\n"

            mac_address = vm.get('mac_address', '')
            if mac_address:
                result += f"- MAC 地址: {mac_address}\n"

            # 账号密码（最重要的信息）
            if show_password:
                result += "\n## 🔑 登录信息\n"
                # 从 credential 字段获取凭据
                credential = vm.get('credential', {})
                if credential:
                    user = credential.get('user', '') or credential.get('username', '') or 'root'
                    password = credential.get('password', '')
                else:
                    user = 'root'
                    password = ''

                if password:
                    result += f"- 用户名: `{user}`\n"
                    result += f"- 密码: `{password}`\n"
                else:
                    result += "- 密码: 未设置或使用模板默认密码\n"

            # 运行状态
            result += "\n## 运行状态\n"
            autostart = vm.get('autostart', False)
            result += f"- 自动启动: {'是' if autostart else '否'}\n"

            uptime = vm.get('uptime', '')
            if uptime:
                result += f"- 运行时间: {uptime}\n"

            return result

        except QVMConsoleAPIError as e:
            logger.error(f"获取虚拟机信息失败: {e}")
            return f"❌ 获取虚拟机信息失败: {str(e)}"

    async def list_vms(self) -> str:
        """
        列出所有虚拟机

        Returns:
            格式化的虚拟机列表
        """
        try:
            vms = await self.client.list_vms()

            if not vms:
                return "当前没有虚拟机"

            result = f"虚拟机列表 (共 {len(vms)} 台):\n\n"

            for i, vm in enumerate(vms, 1):
                name = vm.get('name', '未知')
                status = vm.get('status', '未知')
                vcpu = vm.get('vcpu', 0)
                memory_mb = vm.get('memory', 0)
                memory_gb = memory_mb / 1024 if memory_mb > 0 else 0
                ip_address = vm.get('ip', '无')

                # 状态图标
                state_icon = "🟢" if status == "running" else "🔴" if status == "shut off" else "🟡"

                result += f"{i}. {state_icon} **{name}**\n"
                result += f"   - 状态: {status}\n"
                result += f"   - 配置: {vcpu} 核 / {memory_gb:.1f} GB\n"
                result += f"   - IP: {ip_address}\n\n"

            return result

        except QVMConsoleAPIError as e:
            logger.error(f"获取虚拟机列表失败: {e}")
            return f"❌ 获取虚拟机列表失败: {str(e)}"

    async def edit_vm(
        self,
        vm_name: str,
        vcpu: Optional[int] = None,
        ram: Optional[int] = None,
        remark: Optional[str] = None,
        autostart: Optional[bool] = None
    ) -> str:
        """
        编辑虚拟机配置

        Args:
            vm_name: 虚拟机名称
            vcpu: CPU 核心数
            ram: 内存大小（GB）
            remark: 备注信息
            autostart: 是否自动启动

        Returns:
            编辑结果信息
        """
        try:
            # 构建更新参数
            params = {}
            changes = []

            if vcpu is not None:
                params["vcpu"] = vcpu
                changes.append(f"CPU: {vcpu} 核心")

            if ram is not None:
                params["ram"] = ram
                changes.append(f"内存: {ram} GB")

            if remark is not None:
                params["remark"] = remark
                changes.append(f"备注: {remark}")

            if autostart is not None:
                params["autostart"] = autostart
                changes.append(f"自动启动: {'是' if autostart else '否'}")

            if not params:
                return "❌ 没有指定需要修改的参数"

            # 发送编辑请求
            await self.client.edit_vm(vm_name, params)

            result = f"✅ 虚拟机配置已更新: {vm_name}\n\n"
            result += "修改内容:\n"
            for change in changes:
                result += f"- {change}\n"

            return result

        except QVMConsoleAPIError as e:
            logger.error(f"编辑虚拟机失败: {e}")
            return f"❌ 编辑虚拟机失败: {str(e)}"
