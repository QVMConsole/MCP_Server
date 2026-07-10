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
        列出虚拟机可用的存储位置及可用空间

        Returns:
            格式化的存储位置列表信息
        """
        try:
            result = await self.client.list_storage_pools()

            if not result:
                return "❌ 没有找到可用的存储位置"

            response = "=" * 60 + "\n"
            response += "虚拟机可用存储位置\n"
            response += "=" * 60 + "\n\n"

            for i, pool in enumerate(result, 1):
                pool_id = pool.get("id", "")
                display_name = pool.get("display_name", pool.get("device_path", "未命名"))
                
                # 获取大小信息（单位：字节）
                size_bytes = pool.get("size", 0)
                used_bytes = pool.get("used", 0)
                available_bytes = pool.get("available", 0)
                
                # 转换为 GB
                total_gb = size_bytes / (1024 ** 3) if size_bytes > 0 else 0
                used_gb = used_bytes / (1024 ** 3) if used_bytes > 0 else 0
                available_gb = available_bytes / (1024 ** 3) if available_bytes > 0 else 0
                
                # 计算使用率
                usage_percent = (used_bytes / size_bytes * 100) if size_bytes > 0 else 0
                
                # 状态判断
                enabled = pool.get("enabled", False)
                is_default = pool.get("is_default", False)
                vm_dir = pool.get("vm_dir", "")
                
                # 状态图标
                if enabled:
                    status_icon = "✅ 可用"
                else:
                    status_icon = "⚠️ 已禁用"

                response += f"{i}. {display_name}"
                if is_default:
                    response += " ⭐ (默认)"
                response += f" {status_icon}\n"
                response += f"   - ID: {pool_id}\n"
                response += f"   - 存储目录: {vm_dir}\n"
                response += f"   - 总容量: {total_gb:.2f} GB\n"
                response += f"   - 已使用: {used_gb:.2f} GB\n"
                response += f"   - 可用: {available_gb:.2f} GB\n"
                response += f"   - 使用率: {usage_percent:.1f}%\n"
                response += "\n"

            response += "=" * 60 + "\n"
            response += "💡 提示：创建虚拟机时使用 storage_pool_id 参数指定存储位置\n"
            response += "   不指定则使用默认存储位置（带 ⭐ 标记的）\n"

            return response

        except Exception as e:
            return f"❌ 获取存储位置列表失败: {str(e)}"

    async def list_switches(self) -> str:
        """
        列出所有 VPC 交换机

        Returns:
            格式化的交换机列表信息
        """
        try:
            result = await self.client.list_switches()

            if not result:
                return "❌ 没有找到交换机"

            response = "=" * 60 + "\n"
            response += "VPC 交换机列表\n"
            response += "=" * 60 + "\n\n"

            default_switch = None
            for switch in result:
                if switch.get("is_default", False):
                    default_switch = switch
                    break

            for i, switch in enumerate(result, 1):
                switch_id = switch.get("id", 0)
                name = switch.get("name", "未命名")
                bridge = switch.get("bridge", "")
                is_default = switch.get("is_default", False)

                default_text = " ⭐ (默认)" if is_default else ""

                response += f"{i}. {name}{default_text}\n"
                response += f"   - ID: {switch_id}\n"
                response += f"   - 网桥: {bridge}\n"
                response += f"   - 类型: {'默认交换机' if is_default else '普通交换机'}\n"
                response += "\n"

            response += "=" * 60 + "\n"
            response += "使用建议\n"
            response += "=" * 60 + "\n\n"

            if default_switch:
                response += f"💡 创建虚拟机时建议使用默认交换机：\n"
                response += f"   switch_id: {default_switch.get('id')}\n"
                response += f"   名称: {default_switch.get('name')}\n"
            else:
                response += f"💡 创建虚拟机时建议使用第一个交换机：\n"
                response += f"   switch_id: {result[0].get('id')}\n"
                response += f"   名称: {result[0].get('name')}\n"

            response += "\n示例：\n"
            response += "create_vm_from_template(\n"
            response += "    template_name=\"Ubuntu26.04-LTS\",\n"
            response += "    vm_name=\"test-vm\",\n"
            response += "    vcpu=2,\n"
            response += "    ram=4,\n"
            response += "    user=\"ubuntu\",\n"
            response += "    password=\"Pass123\",\n"
            response += f"    switch_id={default_switch.get('id') if default_switch else result[0].get('id')}  # ← 使用此交换机\n"
            response += ")\n"

            return response

        except Exception as e:
            return f"❌ 获取交换机列表失败: {str(e)}"

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
        storage_pool_id: Optional[str] = None,
        nic_model: Optional[str] = None,
        switch_id: Optional[int] = None,
        security_group_id: Optional[int] = None
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
            nic_model: 网卡模型（virtio/e1000e/rtl8139），不填则使用默认
            switch_id: VPC 交换机 ID，用于 VPC 网络配置
            security_group_id: 安全组 ID，用于防火墙规则配置

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
            if nic_model:
                params["nic_model"] = nic_model
            if switch_id is not None:
                params["switch_id"] = switch_id
            if security_group_id is not None:
                params["security_group_id"] = security_group_id

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
            if nic_model:
                response += f"- 网卡模型: {nic_model}\n"
            if switch_id is not None:
                response += f"- VPC 交换机 ID: {switch_id}\n"
            if security_group_id is not None:
                response += f"- 安全组 ID: {security_group_id}\n"
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

    async def add_disk(
        self,
        vm_name: str,
        size_gb: int,
        format: str = "qcow2",
        bus: str = "virtio"
    ) -> str:
        """
        为虚拟机添加新硬盘

        Args:
            vm_name: 虚拟机名称
            size_gb: 磁盘大小（GB）
            format: 磁盘格式（qcow2/raw）
            bus: 磁盘总线（virtio/scsi/sata/ide）

        Returns:
            添加结果信息
        """
        try:
            result = await self.client.add_disk(vm_name, size_gb, format, bus)
            
            response = f"✅ 硬盘添加成功: {vm_name}\n\n"
            response += f"- 磁盘大小: {size_gb} GB\n"
            response += f"- 磁盘格式: {format}\n"
            response += f"- 磁盘总线: {bus}\n"
            
            # 如果返回了设备名称
            if isinstance(result, dict) and "device" in result:
                response += f"- 设备名称: {result['device']}\n"

            return response

        except QVMConsoleAPIError as e:
            logger.error(f"添加硬盘失败: {e}")
            return f"❌ 添加硬盘失败: {str(e)}"

    async def list_disks(self, vm_name: str) -> str:
        """
        列出虚拟机的所有磁盘

        Args:
            vm_name: 虚拟机名称

        Returns:
            格式化的磁盘列表
        """
        try:
            disks = await self.client.list_disks(vm_name)

            if not disks:
                return f"虚拟机 **{vm_name}** 当前没有磁盘"

            response = f"虚拟机 **{vm_name}** 的磁盘列表:\n\n"

            for i, disk in enumerate(disks, 1):
                dev = disk.get("device", "未知")
                disk_type = disk.get("type", "disk")
                source = disk.get("source", "")
                size_bytes = disk.get("capacity", 0)
                size_gb = size_bytes / (1024 ** 3) if size_bytes > 0 else 0
                bus = disk.get("bus", "未知")
                
                # 图标
                icon = "💾" if disk_type == "disk" else "📀"
                
                response += f"{i}. {icon} **{dev}**\n"
                response += f"   - 类型: {disk_type}\n"
                response += f"   - 大小: {size_gb:.2f} GB\n"
                response += f"   - 总线: {bus}\n"
                if source:
                    response += f"   - 文件: {source}\n"
                response += "\n"

            return response

        except QVMConsoleAPIError as e:
            logger.error(f"获取磁盘列表失败: {e}")
            return f"❌ 获取磁盘列表失败: {str(e)}"

    async def resize_disk(self, vm_name: str, dev: str, size_gb: int) -> str:
        """
        扩容虚拟机磁盘

        Args:
            vm_name: 虚拟机名称
            dev: 设备名称（如 vda, vdb）
            size_gb: 新的大小（GB）

        Returns:
            扩容结果信息
        """
        try:
            await self.client.resize_disk(vm_name, dev, size_gb)

            response = f"✅ 磁盘扩容成功: {vm_name}\n\n"
            response += f"- 设备: {dev}\n"
            response += f"- 新大小: {size_gb} GB\n"
            response += f"\n⚠️ 提示: 扩容后需要在虚拟机内部调整分区大小才能使用新空间\n"

            return response

        except QVMConsoleAPIError as e:
            logger.error(f"磁盘扩容失败: {e}")
            return f"❌ 磁盘扩容失败: {str(e)}"

    async def reset_vm_password(self, vm_name: str, username: str, password: str) -> str:
        """
        重置虚拟机用户密码

        Args:
            vm_name: 虚拟机名称
            username: 用户名
            password: 新密码

        Returns:
            重置结果信息
        """
        try:
            result = await self.client.reset_vm_password(vm_name, username, password)
            task_id = result.get("task_id", "")

            response = f"✅ 密码重置任务已提交: {vm_name}\n\n"
            response += f"- 用户名: {username}\n"
            response += f"- 新密码: {password}\n"
            response += f"\n任务 ID: {task_id}\n"
            response += f"\n⚠️ 提示: 密码重置需要虚拟机处于运行状态，并且支持密码重置功能\n"

            return response

        except QVMConsoleAPIError as e:
            logger.error(f"重置密码失败: {e}")
            return f"❌ 重置密码失败: {str(e)}"

    async def vm_power_operation(self, vm_name: str, action: str) -> str:
        """
        虚拟机电源操作

        Args:
            vm_name: 虚拟机名称
            action: 操作类型 (start/shutdown/destroy/reboot/reset)

        Returns:
            操作结果信息
        """
        try:
            action_map = {
                "start": "启动",
                "shutdown": "关机",
                "destroy": "强制关机",
                "reboot": "重启",
                "reset": "重置"
            }

            action_text = action_map.get(action, action)
            result = await self.client.vm_power_operation(vm_name, action)

            response = f"✅ 虚拟机 {action_text} 指令已下发: {vm_name}\n"
            
            # 检查是否有警告信息
            if isinstance(result, dict) and "warning" in result:
                response += f"\n⚠️ 提示: {result['warning']}\n"

            return response

        except QVMConsoleAPIError as e:
            logger.error(f"虚拟机电源操作失败: {e}")
            return f"❌ 虚拟机 {action_map.get(action, action)} 失败: {str(e)}"

    async def list_snapshots(self, vm_name: str) -> str:
        """
        列出虚拟机快照

        Args:
            vm_name: 虚拟机名称

        Returns:
            格式化的快照列表
        """
        try:
            result = await self.client.list_snapshots(vm_name)
            snapshots = result.get("data", []) if isinstance(result, dict) else result

            if not snapshots:
                return f"虚拟机 **{vm_name}** 当前没有快照"

            response = f"虚拟机 **{vm_name}** 的快照列表:\n\n"

            for i, snap in enumerate(snapshots, 1):
                name = snap.get("name", "未知")
                description = snap.get("description", "")
                created_at = snap.get("created_at", "未知")
                state = snap.get("state", "")
                
                response += f"{i}. **{name}**\n"
                if description:
                    response += f"   - 描述: {description}\n"
                response += f"   - 创建时间: {created_at}\n"
                if state:
                    response += f"   - 状态: {state}\n"
                response += "\n"

            # 显示配额信息
            if isinstance(result, dict) and "quota" in result:
                quota = result["quota"]
                used = quota.get("used", 0)
                limit = quota.get("limit", 0)
                response += f"\n快照配额: {used}/{limit}\n"

            return response

        except QVMConsoleAPIError as e:
            logger.error(f"获取快照列表失败: {e}")
            return f"❌ 获取快照列表失败: {str(e)}"

    async def create_snapshot(
        self,
        vm_name: str,
        snapshot_name: str,
        description: Optional[str] = None,
        include_memory: bool = False,
        auto_fix_nvram: bool = False
    ) -> str:
        """
        创建虚拟机快照

        Args:
            vm_name: 虚拟机名称
            snapshot_name: 快照名称
            description: 快照描述
            include_memory: 是否包含内存状态
            auto_fix_nvram: 自动修复 NVRAM

        Returns:
            创建结果信息
        """
        try:
            params = {
                "name": snapshot_name,
                "include_memory": include_memory,
                "auto_fix_nvram": auto_fix_nvram
            }
            
            if description:
                params["description"] = description

            result = await self.client.create_snapshot(vm_name, params)
            task_id = result.get("task_id", "")

            response = f"✅ 快照创建任务已提交: {vm_name}\n\n"
            response += f"- 快照名称: {snapshot_name}\n"
            if description:
                response += f"- 描述: {description}\n"
            response += f"- 包含内存: {'是' if include_memory else '否'}\n"
            response += f"\n任务 ID: {task_id}\n"

            return response

        except QVMConsoleAPIError as e:
            logger.error(f"创建快照失败: {e}")
            return f"❌ 创建快照失败: {str(e)}"

    async def revert_snapshot(self, vm_name: str, snapshot_name: str) -> str:
        """
        恢复虚拟机快照

        Args:
            vm_name: 虚拟机名称
            snapshot_name: 快照名称

        Returns:
            恢复结果信息
        """
        try:
            result = await self.client.revert_snapshot(vm_name, snapshot_name)
            task_id = result.get("task_id", "")

            response = f"✅ 快照恢复任务已提交: {vm_name}\n\n"
            response += f"- 快照名称: {snapshot_name}\n"
            response += f"\n任务 ID: {task_id}\n"
            response += f"\n⚠️ 提示: 恢复快照会丢失快照之后的所有数据变更\n"

            return response

        except QVMConsoleAPIError as e:
            logger.error(f"恢复快照失败: {e}")
            return f"❌ 恢复快照失败: {str(e)}"

    async def delete_snapshot(self, vm_name: str, snapshot_name: str) -> str:
        """
        删除虚拟机快照

        Args:
            vm_name: 虚拟机名称
            snapshot_name: 快照名称

        Returns:
            删除结果信息
        """
        try:
            result = await self.client.delete_snapshot(vm_name, snapshot_name)
            task_id = result.get("task_id", "")

            response = f"✅ 快照删除任务已提交: {vm_name}\n\n"
            response += f"- 快照名称: {snapshot_name}\n"
            response += f"\n任务 ID: {task_id}\n"

            return response

        except QVMConsoleAPIError as e:
            logger.error(f"删除快照失败: {e}")
            return f"❌ 删除快照失败: {str(e)}"

    async def list_vm_schedules(self, vm_name: str) -> str:
        """
        列出虚拟机定时任务

        Args:
            vm_name: 虚拟机名称

        Returns:
            格式化的定时任务列表
        """
        try:
            schedules = await self.client.list_vm_schedules(vm_name)

            if not schedules:
                return f"虚拟机 **{vm_name}** 当前没有定时任务"

            response = f"虚拟机 **{vm_name}** 的定时任务列表:\n\n"

            for i, schedule in enumerate(schedules, 1):
                schedule_id = schedule.get("id", 0)
                action = schedule.get("action", "未知")
                cron_expr = schedule.get("cron_expr", "")
                enabled = schedule.get("enabled", False)
                remark = schedule.get("remark", "")
                
                status_icon = "✅" if enabled else "❌"
                
                response += f"{i}. {status_icon} ID: {schedule_id}\n"
                response += f"   - 操作: {action}\n"
                response += f"   - Cron 表达式: {cron_expr}\n"
                response += f"   - 状态: {'启用' if enabled else '禁用'}\n"
                if remark:
                    response += f"   - 备注: {remark}\n"
                response += "\n"

            return response

        except QVMConsoleAPIError as e:
            logger.error(f"获取定时任务列表失败: {e}")
            return f"❌ 获取定时任务列表失败: {str(e)}"

    async def create_vm_schedule(
        self,
        vm_name: str,
        action: str,
        schedule_type: str,
        time_of_day: Optional[str] = None,
        run_at: Optional[str] = None,
        weekdays: Optional[List[int]] = None,
        enabled: bool = True,
        timezone: str = "Asia/Shanghai"
    ) -> str:
        """
        创建虚拟机定时任务

        Args:
            vm_name: 虚拟机名称
            action: 操作类型 (start/shutdown/delete)
            schedule_type: 计划类型 (once/daily/weekly)
            time_of_day: 每日执行时间，格式 HH:MM (daily/weekly 使用)
            run_at: 一次性执行时间，格式 YYYY-MM-DD HH:MM:SS (once 使用)
            weekdays: 星期几执行，1-7 表示周一到周日 (weekly 使用)
            enabled: 是否启用
            timezone: 时区

        Returns:
            创建结果信息
        """
        try:
            # 确定事件类型
            if action in ["start", "shutdown"]:
                event_type = "power"
            elif action == "delete":
                event_type = "vm"
            else:
                return f"❌ 不支持的操作类型: {action}，仅支持 start、shutdown、delete"

            # 构建参数
            params = {
                "event_type": event_type,
                "action": action,
                "schedule_type": schedule_type,
                "timezone": timezone,
                "enabled": enabled
            }

            # 根据计划类型添加相应参数
            if schedule_type == "once":
                if not run_at:
                    return "❌ 一次性任务必须指定 run_at 参数（执行时间）"
                params["run_at"] = run_at
            elif schedule_type == "daily":
                if not time_of_day:
                    return "❌ 每日任务必须指定 time_of_day 参数（执行时间）"
                params["time_of_day"] = time_of_day
            elif schedule_type == "weekly":
                if not time_of_day:
                    return "❌ 每周任务必须指定 time_of_day 参数（执行时间）"
                if not weekdays:
                    return "❌ 每周任务必须指定 weekdays 参数（星期几）"
                params["time_of_day"] = time_of_day
                params["weekdays"] = weekdays
            else:
                return f"❌ 不支持的计划类型: {schedule_type}，仅支持 once、daily、weekly"

            result = await self.client.create_vm_schedule(vm_name, params)
            schedule_id = result.get("id", 0)

            response = f"✅ 定时任务已创建: {vm_name}\n\n"
            response += f"- 任务 ID: {schedule_id}\n"
            response += f"- 操作: {action}\n"
            response += f"- 计划类型: {schedule_type}\n"
            
            if schedule_type == "once" and run_at:
                response += f"- 执行时间: {run_at}\n"
            elif schedule_type == "daily" and time_of_day:
                response += f"- 每日执行时间: {time_of_day}\n"
            elif schedule_type == "weekly" and time_of_day and weekdays:
                weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
                weekday_str = "、".join([weekday_names[w-1] for w in weekdays if 1 <= w <= 7])
                response += f"- 每周执行: {weekday_str}\n"
                response += f"- 执行时间: {time_of_day}\n"
            
            response += f"- 时区: {timezone}\n"
            response += f"- 状态: {'启用' if enabled else '禁用'}\n"

            return response

        except QVMConsoleAPIError as e:
            logger.error(f"创建定时任务失败: {e}")
            return f"❌ 创建定时任务失败: {str(e)}"

    async def delete_vm_schedule(self, vm_name: str, schedule_id: int) -> str:
        """
        删除虚拟机定时任务

        Args:
            vm_name: 虚拟机名称
            schedule_id: 定时任务 ID

        Returns:
            删除结果信息
        """
        try:
            await self.client.delete_vm_schedule(vm_name, schedule_id)

            response = f"✅ 定时任务已删除: {vm_name}\n\n"
            response += f"- 任务 ID: {schedule_id}\n"

            return response

        except QVMConsoleAPIError as e:
            logger.error(f"删除定时任务失败: {e}")
            return f"❌ 删除定时任务失败: {str(e)}"

    async def get_vm_stats(self, vm_name: str) -> str:
        """
        获取虚拟机实时监控数据

        Args:
            vm_name: 虚拟机名称

        Returns:
            格式化的监控数据
        """
        try:
            stats = await self.client.get_vm_stats(vm_name)

            response = f"虚拟机 **{vm_name}** 实时监控数据:\n\n"

            # CPU 信息
            cpu_percent = stats.get("cpu_percent", 0)
            response += f"## CPU\n"
            response += f"- 使用率: {cpu_percent:.1f}%\n\n"

            # 内存信息
            memory_used_mb = stats.get("memory_used_mb", 0)
            memory_total_mb = stats.get("memory_total_mb", 0)
            memory_percent = (memory_used_mb / memory_total_mb * 100) if memory_total_mb > 0 else 0
            response += f"## 内存\n"
            response += f"- 已使用: {memory_used_mb:.0f} MB / {memory_total_mb:.0f} MB\n"
            response += f"- 使用率: {memory_percent:.1f}%\n\n"

            # 磁盘信息
            disk_read_mb = stats.get("disk_read_mb", 0)
            disk_write_mb = stats.get("disk_write_mb", 0)
            response += f"## 磁盘 I/O\n"
            response += f"- 读取: {disk_read_mb:.2f} MB\n"
            response += f"- 写入: {disk_write_mb:.2f} MB\n\n"

            # 网络信息
            net_rx_mb = stats.get("net_rx_mb", 0)
            net_tx_mb = stats.get("net_tx_mb", 0)
            response += f"## 网络流量\n"
            response += f"- 接收: {net_rx_mb:.2f} MB\n"
            response += f"- 发送: {net_tx_mb:.2f} MB\n"

            return response

        except QVMConsoleAPIError as e:
            logger.error(f"获取监控数据失败: {e}")
            return f"❌ 获取监控数据失败: {str(e)}"
