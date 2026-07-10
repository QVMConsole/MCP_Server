"""QVMConsole MCP Server - 主入口"""

import asyncio
import sys
from pathlib import Path
from loguru import logger

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

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
        description="列出所有存储池及其可用空间信息。在创建虚拟机时，如果默认存储池空间不足，可以选择其他有足够空间的存储池。",
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
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """调用工具"""
            logger.info(f"调用工具: {name}, 参数: {arguments}")

            try:
                # 根据工具名称分发到对应的处理函数
                if name == "list_templates":
                    result = await tools.list_templates()

                elif name == "list_storage_pools":
                    result = await tools.list_storage_pools()

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
                        storage_pool_id=arguments.get("storage_pool_id")
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
