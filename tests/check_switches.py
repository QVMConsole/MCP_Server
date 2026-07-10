"""
查询 QVMConsole 的交换机（Switch）列表
用于确定创建虚拟机时应该使用哪个 switch_id
"""

import asyncio
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import init_config
from client import QVMConsoleClient


async def main():
    """主函数"""
    print("=" * 60)
    print("查询 QVMConsole 交换机列表")
    print("=" * 60)

    config = init_config()
    client = QVMConsoleClient()

    # 获取交换机列表
    print("\n正在查询交换机列表...")
    print("-" * 60)
    
    try:
        # 调用 VPC 交换机 API
        switches = await client._request("GET", "/api/vpc/switches")
        
        if not switches:
            print("⚠️ 没有找到交换机")
            print("\n说明：QVMConsole 需要配置至少一个交换机才能创建有网络的虚拟机")
            return
        
        print(f"\n找到 {len(switches)} 个交换机：\n")
        
        for i, switch in enumerate(switches, 1):
            switch_id = switch.get("id", 0)
            name = switch.get("name", "未命名")
            is_default = switch.get("is_default", False)
            bridge = switch.get("bridge", "")
            
            default_text = " (默认)" if is_default else ""
            
            print(f"{i}. {name}{default_text}")
            print(f"   - ID: {switch_id}")
            print(f"   - 网桥: {bridge}")
            print(f"   - 状态: {'默认交换机' if is_default else '普通交换机'}")
            print()
        
        # 找到默认交换机
        default_switch = None
        for switch in switches:
            if switch.get("is_default", False):
                default_switch = switch
                break
        
        if default_switch:
            print("=" * 60)
            print("✅ 建议使用的 switch_id")
            print("=" * 60)
            print(f"\nswitch_id: {default_switch.get('id')}")
            print(f"交换机名称: {default_switch.get('name')}")
            print(f"\n创建虚拟机时请使用此 switch_id：")
            print(f"""
create_vm_from_template(
    template_name="debian-13-generic",
    vm_name="test-vm",
    vcpu=4,
    ram=4,
    user="debian",
    password="Pass123",
    nic_model="virtio",
    switch_id={default_switch.get('id')}  # ← 使用默认交换机 ID
)
""")
        else:
            print("=" * 60)
            print("⚠️ 没有找到默认交换机")
            print("=" * 60)
            print(f"\n可以使用第一个交换机的 ID: {switches[0].get('id')}")
            print(f"交换机名称: {switches[0].get('name')}")
    
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        
        if "404" in str(e) or "Not Found" in str(e):
            print("\n可能的原因：")
            print("1. API 路径不正确")
            print("2. QVMConsole 版本不支持此 API")
            print("\n建议：查看 QVMConsole API 文档确认交换机查询接口")
        
        print("\n备选方案：")
        print("如果系统有配置交换机，通常默认交换机 ID 是 1")
        print("可以尝试使用 switch_id=1 创建虚拟机")

    print("\n" + "=" * 60)
    print("查询完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
