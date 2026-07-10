"""
测试 list_switches 工具
验证交换机列表查询功能
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import init_config
from tools import QVMConsoleTools


async def main():
    """主函数"""
    print("=" * 60)
    print("测试 list_switches 工具")
    print("=" * 60)

    config = init_config()
    tools = QVMConsoleTools()

    # 测试查询交换机列表
    print("\n正在查询交换机列表...")
    print("-" * 60)
    
    result = await tools.list_switches()
    print(result)

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
