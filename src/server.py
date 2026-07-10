"""QVMConsole MCP Server - 主入口"""

import asyncio
import sys
from pathlib import Path
from loguru import logger

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent

try:
    from .config import init_config
    from .tools import QVMConsoleTools
except ImportError:
    from config import init_config
    from tools import QVMConsoleTools


# MCP 工具定义
TOOLS = [
    Tool(
        name="list_templates",
        description="列出所有可用的虚拟机模板，包括模板名称、类型、分类等信息",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="list_storage_pools",
        description="列出虚拟机可用的存储位置及其可用空间信息。创建虚拟机时，如果默认存储位置空间不足，可以选择其他有足够空间的存储位置。",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="list_switches",
        description="列出所有 VPC 交换机。创建虚拟机时需要指定 switch_id 才能让虚拟机有网络连接。使用此工具查看可用的交换机 ID。",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="create_vm_from_template",
        description="从模板创建虚拟机。创建成功后会返回任务ID，可以使用 get_vm_info 查看虚拟机详情和登录密码。",
        inputSchema={
            "type": "object",
            "properties": {
                "template_name": {
                    "type": "string",
                    "description": "模板名称，可以通过 list_templates 获取可用模板列表"
                },
                "vm_name": {
                    "type": "string",
                    "description": "虚拟机名称，必须唯一"
                },
                "vcpu": {
                    "type": "integer",
                    "description": "CPU 核心数",
                    "minimum": 1
                },
                "ram": {
                    "type": "integer",
                    "description": "内存大小（GB）",
                    "minimum": 1
                },
                "disk_size": {
                    "type": "integer",
                    "description": "磁盘大小（GB），不填则使用模板默认值",
                    "minimum": 1
                },
                "hostname": {
                    "type": "string",
                    "description": "主机名，不填则使用虚拟机名称"
                },
                "password": {
                    "type": "string",
                    "description": "登录密码，不填则自动生成随机密码"
                },
                "user": {
                    "type": "string",
                    "description": "用户名，不填则使用模板默认用户"
                },
                "autostart": {
                    "type": "boolean",
                    "description": "是否创建后自动启动虚拟机",
                    "default": False
                },
                "remark": {
                    "type": "string",
                    "description": "备注信息"
                },
                "storage_pool_id": {
                    "type": "string",
                    "description": "存储池 ID，不填则使用默认存储池。如果默认存储池空间不足，可以通过 list_storage_pools 查看其他可用存储池并指定此参数。"
                },
                "nic_model": {
                    "type": "string",
                    "description": "网卡模型，可选值：virtio（推荐，性能最好）、e1000e（兼容性好）、rtl8139（旧系统兼容）。不填则使用默认配置。",
                    "enum": ["virtio", "e1000e", "rtl8139"]
                },
                "switch_id": {
                    "type": "integer",
                    "description": "VPC 交换机 ID，用于将虚拟机加入特定的 VPC 网络。不填则使用默认网络。"
                },
                "security_group_id": {
                    "type": "integer",
                    "description": "安全组 ID，用于配置虚拟机的防火墙规则。不填则使用默认安全组。"
                }
            },
            "required": ["template_name", "vm_name", "vcpu", "ram"]
        }
    ),
    Tool(
        name="get_vm_info",
        description="获取虚拟机的详细信息，包括配置、网络信息、运行状态和登录密码等。这是查看虚拟机密码的主要方式。",
        inputSchema={
            "type": "object",
            "properties": {
                "vm_name": {
                    "type": "string",
                    "description": "虚拟机名称"
                },
                "show_password": {
                    "type": "boolean",
                    "description": "是否显示密码信息",
                    "default": True
                }
            },
            "required": ["vm_name"]
        }
    ),
    Tool(
        name="list_vms",
        description="列出所有虚拟机及其基本状态信息",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="edit_vm",
        description="编辑虚拟机配置，可以修改 CPU、内存、备注等信息。注意：某些修改需要关机后才能生效。",
        inputSchema={
            "type": "object",
            "properties": {
                "vm_name": {
                    "type": "string",
                    "description": "虚拟机名称"
                },
                "vcpu": {
                    "type": "integer",
                    "description": "CPU 核心数",
                    "minimum": 1
                },
                "ram": {
                    "type": "integer",
                    "description": "内存大小（GB）",
                    "minimum": 1
                },
                "remark": {
                    "type": "string",
                    "description": "备注信息"
                },
                "autostart": {
                    "type": "boolean",
                    "description": "是否自动启动"
                }
            },
            "required": ["vm_name"]
        }
    ),
    Tool(
        name="add_disk",
        description="为虚拟机添加新的数据硬盘。",
        inputSchema={
            "type": "object",
            "properties": {
                "vm_name": {
                    "type": "string",
                    "description": "虚拟机名称"
                },
                "size_gb": {
                    "type": "integer",
                    "description": "磁盘大小（GB）",
                    "minimum": 1
                },
                "format": {
                    "type": "string",
                    "description": "磁盘格式：qcow2（推荐，支持快照）或 raw（性能更好）",
                    "enum": ["qcow2", "raw"],
                    "default": "qcow2"
                },
                "bus": {
                    "type": "string",
                    "description": "磁盘总线：virtio（推荐）、scsi、sata、ide",
                    "enum": ["virtio", "scsi", "sata", "ide"],
                    "default": "virtio"
                }
            },
            "required": ["vm_name", "size_gb"]
        }
    ),
    Tool(
        name="list_disks",
        description="列出虚拟机的所有磁盘信息。",
        inputSchema={
            "type": "object",
            "properties": {
                "vm_name": {
                    "type": "string",
                    "description": "虚拟机名称"
                }
            },
            "required": ["vm_name"]
        }
    ),
    Tool(
        name="resize_disk",
        description="扩容虚拟机磁盘（只能扩大，不能缩小）。",
        inputSchema={
            "type": "object",
            "properties": {
                "vm_name": {
                    "type": "string",
                    "description": "虚拟机名称"
                },
                "dev": {
                    "type": "string",
                    "description": "设备名称，例如 vda、vdb、vdc"
                },
                "size_gb": {
                    "type": "integer",
                    "description": "新的磁盘大小（GB），必须大于当前大小",
                    "minimum": 1
                }
            },
            "required": ["vm_name", "dev", "size_gb"]
        }
    ),
    Tool(
        name="reset_vm_password",
        description="重置虚拟机用户密码。需要虚拟机处于运行状态。",
        inputSchema={
            "type": "object",
            "properties": {
                "vm_name": {
                    "type": "string",
                    "description": "虚拟机名称"
                },
                "username": {
                    "type": "string",
                    "description": "用户名"
                },
                "password": {
                    "type": "string",
                    "description": "新密码"
                }
            },
            "required": ["vm_name", "username", "password"]
        }
    ),
    Tool(
        name="vm_power_operation",
        description="虚拟机电源操作，支持启动、关机、强制关机、重启、重置等操作。",
        inputSchema={
            "type": "object",
            "properties": {
                "vm_name": {
                    "type": "string",
                    "description": "虚拟机名称"
                },
                "action": {
                    "type": "string",
                    "description": "操作类型",
                    "enum": ["start", "shutdown", "destroy", "reboot", "reset"]
                }
            },
            "required": ["vm_name", "action"]
        }
    ),
    Tool(
        name="list_snapshots",
        description="列出虚拟机的所有快照及配额信息",
        inputSchema={
            "type": "object",
            "properties": {
                "vm_name": {
                    "type": "string",
                    "description": "虚拟机名称"
                }
            },
            "required": ["vm_name"]
        }
    ),
    Tool(
        name="create_snapshot",
        description="创建虚拟机快照。快照可以保存虚拟机的当前状态，便于后续恢复。",
        inputSchema={
            "type": "object",
            "properties": {
                "vm_name": {
                    "type": "string",
                    "description": "虚拟机名称"
                },
                "snapshot_name": {
                    "type": "string",
                    "description": "快照名称"
                },
                "description": {
                    "type": "string",
                    "description": "快照描述"
                },
                "include_memory": {
                    "type": "boolean",
                    "description": "是否包含内存状态（可以保存运行中虚拟机的完整状态）",
                    "default": False
                },
                "auto_fix_nvram": {
                    "type": "boolean",
                    "description": "自动修复 UEFI NVRAM（UEFI 虚拟机需要开启）",
                    "default": False
                }
            },
            "required": ["vm_name", "snapshot_name"]
        }
    ),
    Tool(
        name="revert_snapshot",
        description="恢复虚拟机到指定快照的状态。警告：这将丢失快照之后的所有数据变更。",
        inputSchema={
            "type": "object",
            "properties": {
                "vm_name": {
                    "type": "string",
                    "description": "虚拟机名称"
                },
                "snapshot_name": {
                    "type": "string",
                    "description": "快照名称"
                }
            },
            "required": ["vm_name", "snapshot_name"]
        }
    ),
    Tool(
        name="delete_snapshot",
        description="删除虚拟机快照",
        inputSchema={
            "type": "object",
            "properties": {
                "vm_name": {
                    "type": "string",
                    "description": "虚拟机名称"
                },
                "snapshot_name": {
                    "type": "string",
                    "description": "快照名称"
                }
            },
            "required": ["vm_name", "snapshot_name"]
        }
    ),
    Tool(
        name="list_vm_schedules",
        description="列出虚拟机的所有定时任务",
        inputSchema={
            "type": "object",
            "properties": {
                "vm_name": {
                    "type": "string",
                    "description": "虚拟机名称"
                }
            },
            "required": ["vm_name"]
        }
    ),
    Tool(
        name="create_vm_schedule",
        description="创建虚拟机定时任务，可以定时执行启动、关机、删除等操作。",
        inputSchema={
            "type": "object",
            "properties": {
                "vm_name": {
                    "type": "string",
                    "description": "虚拟机名称"
                },
                "action": {
                    "type": "string",
                    "description": "操作类型",
                    "enum": ["start", "shutdown", "delete"]
                },
                "schedule_type": {
                    "type": "string",
                    "description": "计划类型：once(一次性), daily(每日), weekly(每周)",
                    "enum": ["once", "daily", "weekly"]
                },
                "time_of_day": {
                    "type": "string",
                    "description": "每日执行时间，格式 HH:MM，例如 '02:00'（daily 和 weekly 必填）"
                },
                "run_at": {
                    "type": "string",
                    "description": "一次性执行时间，格式 'YYYY-MM-DD HH:MM:SS'，例如 '2024-12-31 23:59:00'（once 必填）"
                },
                "weekdays": {
                    "type": "array",
                    "description": "星期几执行，1-7 表示周一到周日，例如 [1,3,5] 表示周一、三、五（weekly 必填）",
                    "items": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 7
                    }
                },
                "enabled": {
                    "type": "boolean",
                    "description": "是否启用",
                    "default": True
                },
                "timezone": {
                    "type": "string",
                    "description": "时区，默认 Asia/Shanghai",
                    "default": "Asia/Shanghai"
                }
            },
            "required": ["vm_name", "action", "schedule_type"]
        }
    ),
    Tool(
        name="delete_vm_schedule",
        description="删除虚拟机定时任务",
        inputSchema={
            "type": "object",
            "properties": {
                "vm_name": {
                    "type": "string",
                    "description": "虚拟机名称"
                },
                "schedule_id": {
                    "type": "integer",
                    "description": "定时任务 ID"
                }
            },
            "required": ["vm_name", "schedule_id"]
        }
    ),
    Tool(
        name="get_vm_stats",
        description="获取虚拟机实时监控数据，包括 CPU、内存、磁盘 I/O、网络流量等信息。",
        inputSchema={
            "type": "object",
            "properties": {
                "vm_name": {
                    "type": "string",
                    "description": "虚拟机名称"
                }
            },
            "required": ["vm_name"]
        }
    ),
    Tool(
        name="vnc_status",
        description="查看虚拟机 VNC 状态，包括是否已启用、端口、认证方式等信息。",
        inputSchema={
            "type": "object",
            "properties": {
                "vm_name": {
                    "type": "string",
                    "description": "虚拟机名称"
                }
            },
            "required": ["vm_name"]
        }
    ),
    Tool(
        name="vnc_enable",
        description="开启虚拟机 VNC。开启后可以使用 vnc_screenshot 截图或其他 VNC 操作工具。",
        inputSchema={
            "type": "object",
            "properties": {
                "vm_name": {
                    "type": "string",
                    "description": "虚拟机名称"
                },
                "password": {
                    "type": "string",
                    "description": "VNC 密码（可选，不填则无密码保护）"
                }
            },
            "required": ["vm_name"]
        }
    ),
    Tool(
        name="vnc_expose",
        description="切换 VNC 对外暴露状态。默认 VNC 仅本地访问(127.0.0.1)，如需远程访问需要暴露到 0.0.0.0。注意：这是一个安全敏感操作。",
        inputSchema={
            "type": "object",
            "properties": {
                "vm_name": {
                    "type": "string",
                    "description": "虚拟机名称"
                },
                "expose": {
                    "type": "boolean",
                    "description": "True=对外暴露(0.0.0.0)，False=仅本地(127.0.0.1)，默认 True",
                    "default": True
                }
            },
            "required": ["vm_name"]
        }
    ),
    Tool(
        name="vnc_screenshot",
        description="截取虚拟机 VNC 画面。可以看到虚拟机当前的屏幕内容。需要虚拟机已开启 VNC 并处于运行状态。",
        inputSchema={
            "type": "object",
            "properties": {
                "vm_name": {
                    "type": "string",
                    "description": "虚拟机名称"
                }
            },
            "required": ["vm_name"]
        }
    ),
    Tool(
        name="vnc_click",
        description="在 VNC 画面上点击鼠标。用于模拟鼠标点击操作，可以点击按钮、链接等元素。",
        inputSchema={
            "type": "object",
            "properties": {
                "vm_name": {
                    "type": "string",
                    "description": "虚拟机名称"
                },
                "x": {
                    "type": "integer",
                    "description": "横坐标（像素）",
                    "minimum": 0
                },
                "y": {
                    "type": "integer",
                    "description": "纵坐标（像素）",
                    "minimum": 0
                },
                "button": {
                    "type": "string",
                    "description": "鼠标按键：left（左键）、right（右键）、middle（中键）",
                    "enum": ["left", "right", "middle"],
                    "default": "left"
                }
            },
            "required": ["vm_name", "x", "y"]
        }
    ),
    Tool(
        name="vnc_type",
        description="在 VNC 中输入文本。用于在虚拟机中输入字符串，例如命令、文本内容等。",
        inputSchema={
            "type": "object",
            "properties": {
                "vm_name": {
                    "type": "string",
                    "description": "虚拟机名称"
                },
                "text": {
                    "type": "string",
                    "description": "要输入的文本内容"
                }
            },
            "required": ["vm_name", "text"]
        }
    ),
    Tool(
        name="vnc_key",
        description="在 VNC 中按下特殊按键。用于按下回车、ESC、方向键等特殊按键。",
        inputSchema={
            "type": "object",
            "properties": {
                "vm_name": {
                    "type": "string",
                    "description": "虚拟机名称"
                },
                "key": {
                    "type": "string",
                    "description": "按键名称：enter（回车）、esc（退出）、tab（制表）、backspace（退格）、delete（删除）、up/down/left/right（方向键）、space（空格）、ctrl/alt/shift（功能键）、f1-f12（功能键）"
                }
            },
            "required": ["vm_name", "key"]
        }
    ),
    Tool(
        name="vnc_move",
        description="在 VNC 中移动鼠标到指定位置。用于移动鼠标光标，通常在点击前使用。",
        inputSchema={
            "type": "object",
            "properties": {
                "vm_name": {
                    "type": "string",
                    "description": "虚拟机名称"
                },
                "x": {
                    "type": "integer",
                    "description": "横坐标（像素）",
                    "minimum": 0
                },
                "y": {
                    "type": "integer",
                    "description": "纵坐标（像素）",
                    "minimum": 0
                }
            },
            "required": ["vm_name", "x", "y"]
        }
    )
]


def setup_logging(log_file: str, log_level: str):
    """配置日志"""
    # 移除默认的 handler
    logger.remove()

    # 添加控制台输出（stderr，避免干扰 MCP stdio 通信）
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )

    # 添加文件输出
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger.add(
        log_file,
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days"
    )


async def main():
    """主函数"""
    try:
        # 初始化配置
        config = init_config()
        logger.info(f"配置加载成功: {config.config_path}")

        # 设置日志
        setup_logging(config.log_file, config.log_level)
        logger.info(f"QVMConsole MCP Server v{config.version} 启动中...")
        logger.info(f"连接到 QVMConsole: {config.base_url}")

        # 创建 MCP Server
        server = Server(config.server_name)

        # 初始化工具集
        tools = QVMConsoleTools()

        @server.list_tools()
        async def list_tools() -> list[Tool]:
            """列出所有可用工具"""
            return TOOLS

        @server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent | ImageContent]:
            """调用工具"""
            logger.info(f"调用工具: {name}, 参数: {arguments}")

            try:
                # 根据工具名称分发到对应的处理函数
                if name == "list_templates":
                    result = await tools.list_templates()

                elif name == "list_storage_pools":
                    result = await tools.list_storage_pools()

                elif name == "list_switches":
                    result = await tools.list_switches()

                elif name == "create_vm_from_template":
                    result = await tools.create_vm_from_template(
                        template_name=arguments["template_name"],
                        vm_name=arguments["vm_name"],
                        vcpu=arguments["vcpu"],
                        ram=arguments["ram"],
                        disk_size=arguments.get("disk_size"),
                        hostname=arguments.get("hostname"),
                        password=arguments.get("password"),
                        user=arguments.get("user"),
                        autostart=arguments.get("autostart", False),
                        remark=arguments.get("remark"),
                        storage_pool_id=arguments.get("storage_pool_id"),
                        nic_model=arguments.get("nic_model"),
                        switch_id=arguments.get("switch_id"),
                        security_group_id=arguments.get("security_group_id")
                    )

                elif name == "get_vm_info":
                    result = await tools.get_vm_info(
                        vm_name=arguments["vm_name"],
                        show_password=arguments.get("show_password", True)
                    )

                elif name == "list_vms":
                    result = await tools.list_vms()

                elif name == "edit_vm":
                    result = await tools.edit_vm(
                        vm_name=arguments["vm_name"],
                        vcpu=arguments.get("vcpu"),
                        ram=arguments.get("ram"),
                        remark=arguments.get("remark"),
                        autostart=arguments.get("autostart")
                    )

                elif name == "add_disk":
                    result = await tools.add_disk(
                        vm_name=arguments["vm_name"],
                        size_gb=arguments["size_gb"],
                        format=arguments.get("format", "qcow2"),
                        bus=arguments.get("bus", "virtio")
                    )

                elif name == "list_disks":
                    result = await tools.list_disks(
                        vm_name=arguments["vm_name"]
                    )

                elif name == "resize_disk":
                    result = await tools.resize_disk(
                        vm_name=arguments["vm_name"],
                        dev=arguments["dev"],
                        size_gb=arguments["size_gb"]
                    )

                elif name == "reset_vm_password":
                    result = await tools.reset_vm_password(
                        vm_name=arguments["vm_name"],
                        username=arguments["username"],
                        password=arguments["password"]
                    )

                elif name == "vm_power_operation":
                    result = await tools.vm_power_operation(
                        vm_name=arguments["vm_name"],
                        action=arguments["action"]
                    )

                elif name == "list_snapshots":
                    result = await tools.list_snapshots(
                        vm_name=arguments["vm_name"]
                    )

                elif name == "create_snapshot":
                    result = await tools.create_snapshot(
                        vm_name=arguments["vm_name"],
                        snapshot_name=arguments["snapshot_name"],
                        description=arguments.get("description"),
                        include_memory=arguments.get("include_memory", False),
                        auto_fix_nvram=arguments.get("auto_fix_nvram", False)
                    )

                elif name == "revert_snapshot":
                    result = await tools.revert_snapshot(
                        vm_name=arguments["vm_name"],
                        snapshot_name=arguments["snapshot_name"]
                    )

                elif name == "delete_snapshot":
                    result = await tools.delete_snapshot(
                        vm_name=arguments["vm_name"],
                        snapshot_name=arguments["snapshot_name"]
                    )

                elif name == "list_vm_schedules":
                    result = await tools.list_vm_schedules(
                        vm_name=arguments["vm_name"]
                    )

                elif name == "create_vm_schedule":
                    result = await tools.create_vm_schedule(
                        vm_name=arguments["vm_name"],
                        action=arguments["action"],
                        schedule_type=arguments["schedule_type"],
                        time_of_day=arguments.get("time_of_day"),
                        run_at=arguments.get("run_at"),
                        weekdays=arguments.get("weekdays"),
                        enabled=arguments.get("enabled", True),
                        timezone=arguments.get("timezone", "Asia/Shanghai")
                    )

                elif name == "delete_vm_schedule":
                    result = await tools.delete_vm_schedule(
                        vm_name=arguments["vm_name"],
                        schedule_id=arguments["schedule_id"]
                    )

                elif name == "get_vm_stats":
                    result = await tools.get_vm_stats(
                        vm_name=arguments["vm_name"]
                    )

                elif name == "vnc_status":
                    result = await tools.vnc_status(
                        vm_name=arguments["vm_name"]
                    )

                elif name == "vnc_enable":
                    result = await tools.vnc_enable(
                        vm_name=arguments["vm_name"],
                        password=arguments.get("password")
                    )

                elif name == "vnc_expose":
                    result = await tools.vnc_expose(
                        vm_name=arguments["vm_name"],
                        expose=arguments.get("expose", True)
                    )

                elif name == "vnc_screenshot":
                    # VNC 截图返回图片 + 文本
                    img_base64 = await tools.vnc.screenshot(arguments["vm_name"])
                    
                    # 返回图片内容和文本说明
                    return [
                        TextContent(
                            type="text",
                            text=f"✅ VNC 截图成功: {arguments['vm_name']}"
                        ),
                        ImageContent(
                            type="image",
                            data=img_base64,
                            mimeType="image/png"
                        )
                    ]

                elif name == "vnc_click":
                    result = await tools.vnc_click(
                        vm_name=arguments["vm_name"],
                        x=arguments["x"],
                        y=arguments["y"],
                        button=arguments.get("button", "left")
                    )

                elif name == "vnc_type":
                    result = await tools.vnc_type(
                        vm_name=arguments["vm_name"],
                        text=arguments["text"]
                    )

                elif name == "vnc_key":
                    result = await tools.vnc_key(
                        vm_name=arguments["vm_name"],
                        key=arguments["key"]
                    )

                elif name == "vnc_move":
                    result = await tools.vnc_move(
                        vm_name=arguments["vm_name"],
                        x=arguments["x"],
                        y=arguments["y"]
                    )

                else:
                    result = f"❌ 未知的工具: {name}"

                logger.info(f"工具 {name} 执行成功")
                return [TextContent(type="text", text=result)]

            except Exception as e:
                logger.exception(f"工具 {name} 执行失败")
                error_msg = f"❌ 执行失败: {str(e)}"
                return [TextContent(type="text", text=error_msg)]

        # 启动 MCP Server（使用 stdio 传输）
        logger.info("MCP Server 已启动，等待客户端连接...")
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )

    except FileNotFoundError as e:
        logger.error(f"配置文件错误: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"配置错误: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception("启动失败")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
