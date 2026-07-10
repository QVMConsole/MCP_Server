#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Interactive MCP Client - List and manage VMs"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import init_config
from tools import QVMConsoleTools
from loguru import logger

logger.remove()
logger.add(sys.stderr, level="INFO", format="<level>{level: <8}</level> | {message}")


async def show_menu():
    """Display menu"""
    print("\n=== QVMConsole MCP Client ===")
    print("1. List all VMs")
    print("2. List templates")
    print("3. Get VM info")
    print("4. Exit")
    return input("Select option (1-4): ").strip()


async def list_vms_cmd(tools):
    """List all virtual machines"""
    print("\n--- Virtual Machines ---")
    result = await tools.list_vms()
    print(result)


async def list_templates_cmd(tools):
    """List all templates"""
    print("\n--- Available Templates ---")
    result = await tools.list_templates()
    print(result)


async def get_vm_info_cmd(tools):
    """Get VM information"""
    vm_name = input("Enter VM name: ").strip()
    if not vm_name:
        print("VM name cannot be empty")
        return
    result = await tools.get_vm_info(vm_name, show_password=True)
    print(result)


async def main():
    """Main function"""
    try:
        init_config()
        tools = QVMConsoleTools()

        while True:
            choice = await show_menu()

            if choice == "1":
                await list_vms_cmd(tools)
            elif choice == "2":
                await list_templates_cmd(tools)
            elif choice == "3":
                await get_vm_info_cmd(tools)
            elif choice == "4":
                print("Goodbye!")
                break
            else:
                print("Invalid option, try again")

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
