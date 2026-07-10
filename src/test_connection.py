#!/usr/bin/env python3
"""
快速测试脚本 - 用于验证 MCP Server 基本功能
"""

import asyncio
import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import init_config, get_config
from client import QVMConsoleClient, QVMConsoleAPIError
from tools import QVMConsoleTools


async def test_connection():
    """测试与 QVMConsole 的连接"""
    print("=" * 60)
    print("QVMConsole MCP Server - 连接测试")
    print("=" * 60)

    try:
        # 初始化配置
        print("\n[1/4] 加载配置文件...")
        config = init_config()
        print(f"✅ 配置加载成功")
        print(f"    - QVMConsole URL: {config.base_url}")
        print(f"    - API Key ID: {config.api_key_id[:20]}...")

        # 创建客户端
        print("\n[2/4] 创建 API 客户端...")
        client = QVMConsoleClient()
        print("✅ 客户端创建成功")

        # 测试获取模板列表
        print("\n[3/4] 测试 API 连接（获取模板列表）...")
        templates = await client.list_templates()
        print(f"✅ API 连接成功，获取到 {len(templates)} 个模板")

        if templates:
            print("\n可用模板：")
            for i, tpl in enumerate(templates[:5], 1):
                name = tpl.get('name', '未知')
                display_name = tpl.get('display_name', name)
                tpl_type = tpl.get('type', '未知')
                print(f"  {i}. {display_name} ({name}) - {tpl_type}")
            if len(templates) > 5:
                print(f"  ... 还有 {len(templates) - 5} 个模板")

        # 测试获取虚拟机列表
        print("\n[4/4] 测试获取虚拟机列表...")
        vms = await client.list_vms()
        print(f"✅ 获取成功，当前有 {len(vms)} 台虚拟机")

        if vms:
            print("\n虚拟机列表：")
            for i, vm in enumerate(vms[:5], 1):
                name = vm.get('name', '未知')
                state = vm.get('state', '未知')
                vcpu = vm.get('vcpu', 0)
                memory_gb = vm.get('memory', 0) / 1024
                print(f"  {i}. {name} - {state} ({vcpu}核/{memory_gb:.1f}GB)")
            if len(vms) > 5:
                print(f"  ... 还有 {len(vms) - 5} 台虚拟机")

        print("\n" + "=" * 60)
        print("✅ 所有测试通过！MCP Server 可以正常使用")
        print("=" * 60)
        print("\n下一步：")
        print("1. 配置 Claude Desktop（参考 QUICKSTART.md）")
        print("2. 重启 Claude Desktop")
        print("3. 在 Claude 中输入：列出所有虚拟机模板")

        return True

    except FileNotFoundError as e:
        print(f"\n❌ 配置文件错误: {e}")
        print("\n解决方法：")
        print("  1. 复制配置文件模板：")
        print("     cp config/config.example.json config/config.json")
        print("  2. 编辑 config/config.json，填入正确的配置")
        return False

    except ValueError as e:
        print(f"\n❌ 配置错误: {e}")
        print("\n解决方法：")
        print("  检查 config/config.json 中的 API Key 配置是否正确")
        return False

    except QVMConsoleAPIError as e:
        print(f"\n❌ API 调用失败: {e}")
        print("\n可能的原因：")
        print("  1. API Key 无效或已被撤销")
        print("  2. QVMConsole 服务未运行")
        print("  3. base_url 配置错误")
        print("  4. 网络连接问题")
        return False

    except Exception as e:
        print(f"\n❌ 发生未知错误: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_tools():
    """测试工具模块"""
    print("\n\n" + "=" * 60)
    print("测试工具模块")
    print("=" * 60)

    try:
        tools = QVMConsoleTools()

        print("\n测试 list_templates 工具...")
        result = await tools.list_templates()
        print("✅ list_templates 工具测试通过")
        print(result[:200] + "..." if len(result) > 200 else result)

        print("\n测试 list_vms 工具...")
        result = await tools.list_vms()
        print("✅ list_vms 工具测试通过")
        print(result[:200] + "..." if len(result) > 200 else result)

        return True

    except Exception as e:
        print(f"❌ 工具测试失败: {e}")
        return False


def main():
    """主函数"""
    print("\n")
    print("*" * 60)
    print("*" + " " * 58 + "*")
    print("*" + "  QVMConsole MCP Server - 快速测试工具".center(56) + "*")
    print("*" + " " * 58 + "*")
    print("*" * 60)

    # 运行异步测试
    result1 = asyncio.run(test_connection())

    if result1:
        result2 = asyncio.run(test_tools())

        if result2:
            print("\n✅ 所有测试完成！")
            sys.exit(0)

    print("\n❌ 测试失败，请检查配置")
    sys.exit(1)


if __name__ == "__main__":
    main()
