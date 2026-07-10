"""VNC 控制器 - 实现 VNC 连接和操作控制"""

import asyncio
import base64
import io
import tempfile
from typing import Optional, Tuple
from loguru import logger
from PIL import Image

try:
    from .client import QVMConsoleClient, QVMConsoleAPIError
except ImportError:
    from client import QVMConsoleClient, QVMConsoleAPIError


class VNCController:
    """VNC 控制器 - 负责截图和操作"""

    def __init__(self, client: QVMConsoleClient):
        """
        初始化 VNC 控制器

        Args:
            client: QVMConsole API 客户端
        """
        self.client = client
        self._vnc_clients = {}  # 缓存 VNC 连接

    async def _get_vnc_connection_info(self, vm_name: str) -> Tuple[str, int]:
        """
        获取 VNC 连接信息

        Args:
            vm_name: 虚拟机名称

        Returns:
            (host, port) 元组

        Raises:
            Exception: 如果 VNC 未开启或获取信息失败
        """
        try:
            vnc_status = await self.client.get_vnc_status(vm_name)
            
            if not vnc_status.get("enabled", False):
                raise Exception(f"虚拟机 {vm_name} 的 VNC 未开启，请先开启 VNC")

            port_str = vnc_status.get("port", "")
            if not port_str:
                raise Exception(f"无法获取虚拟机 {vm_name} 的 VNC 端口")

            # 端口格式可能是：
            # - "5900"
            # - "127.0.0.1:5900"
            # - "5900 (ipv4)" 或 "5900 (ipv6)"
            
            # 移除可能存在的 (ipv4) 或 (ipv6) 后缀
            port_str = port_str.split("(")[0].strip()
            
            if ":" in port_str:
                # 格式: "127.0.0.1:5900"
                host, port = port_str.rsplit(":", 1)
            else:
                # 格式: "5900"
                # 注意：如果 MCP Server 不在 QVMConsole 宿主机上，需要使用 QVMConsole 的主机地址
                # 这里我们尝试从 base_url 中提取主机地址
                base_url = self.client.base_url
                if "://" in base_url:
                    # 提取主机地址，例如 "http://192.168.1.100:8082" -> "192.168.1.100"
                    host = base_url.split("://")[1].split(":")[0]
                else:
                    host = base_url.split(":")[0]
                port = port_str

            return host, int(port)

        except QVMConsoleAPIError as e:
            logger.error(f"获取 VNC 连接信息失败: {e}")
            raise Exception(f"获取 VNC 连接信息失败: {str(e)}")

    async def screenshot(self, vm_name: str) -> str:
        """
        截取 VNC 画面

        Args:
            vm_name: 虚拟机名称

        Returns:
            base64 编码的 PNG 图像

        Raises:
            Exception: 截图失败
        """
        try:
            # 动态导入 vncdotool
            try:
                from vncdotool import api
            except ImportError:
                raise Exception(
                    "vncdotool 库未安装，请运行: pip install vncdotool"
                )

            # 获取 VNC 连接信息
            host, port = await self._get_vnc_connection_info(vm_name)
            
            logger.info(f"正在连接 VNC: {host}:{port}")

            # 连接 VNC
            client = await asyncio.wait_for(
                asyncio.to_thread(api.connect, f"{host}::{port}"),
                timeout=10.0
            )

            # 创建临时文件保存截图
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = tmp.name

            # 截图
            await asyncio.to_thread(client.captureScreen, tmp_path)
            
            # 读取图片并转换为 base64
            with open(tmp_path, "rb") as f:
                img_data = f.read()
            
            # 删除临时文件
            import os
            os.unlink(tmp_path)

            # 转换为 base64
            img_base64 = base64.b64encode(img_data).decode("utf-8")
            
            logger.info(f"VNC 截图成功: {vm_name}")
            return img_base64

        except asyncio.TimeoutError:
            raise Exception(f"连接 VNC 超时: {vm_name}")
        except Exception as e:
            logger.error(f"VNC 截图失败: {e}")
            raise Exception(f"截图失败: {str(e)}")

    async def click(self, vm_name: str, x: int, y: int, button: str = "left") -> None:
        """
        在指定坐标点击鼠标

        Args:
            vm_name: 虚拟机名称
            x: 横坐标
            y: 纵坐标
            button: 鼠标按键 (left/right/middle)

        Raises:
            Exception: 操作失败
        """
        try:
            from vncdotool import api
        except ImportError:
            raise Exception("vncdotool 库未安装，请运行: pip install vncdotool")

        try:
            host, port = await self._get_vnc_connection_info(vm_name)
            
            logger.info(f"VNC 鼠标点击: {vm_name} ({x}, {y}) button={button}")

            # 连接 VNC
            client = await asyncio.wait_for(
                asyncio.to_thread(api.connect, f"{host}::{port}"),
                timeout=10.0
            )

            # 移动鼠标到目标位置
            await asyncio.to_thread(client.mouseMove, x, y)
            
            # 等待一小段时间确保移动完成
            await asyncio.sleep(0.1)

            # 点击
            button_map = {"left": 1, "middle": 2, "right": 3}
            button_num = button_map.get(button.lower(), 1)
            
            await asyncio.to_thread(client.mousePress, button_num)
            
            logger.info(f"VNC 点击成功: {vm_name}")

        except asyncio.TimeoutError:
            raise Exception(f"连接 VNC 超时: {vm_name}")
        except Exception as e:
            logger.error(f"VNC 点击失败: {e}")
            raise Exception(f"点击失败: {str(e)}")

    async def type_text(self, vm_name: str, text: str) -> None:
        """
        输入文本

        Args:
            vm_name: 虚拟机名称
            text: 要输入的文本

        Raises:
            Exception: 操作失败
        """
        try:
            from vncdotool import api
        except ImportError:
            raise Exception("vncdotool 库未安装，请运行: pip install vncdotool")

        try:
            host, port = await self._get_vnc_connection_info(vm_name)
            
            logger.info(f"VNC 输入文本: {vm_name} text_length={len(text)}")

            # 连接 VNC
            client = await asyncio.wait_for(
                asyncio.to_thread(api.connect, f"{host}::{port}"),
                timeout=10.0
            )

            # vncdotool 的 keyPress 需要逐个字符输入
            # 或者使用 type 方法（如果支持）
            for char in text:
                await asyncio.to_thread(client.keyPress, char)
                # 短暂延迟，避免输入过快
                await asyncio.sleep(0.01)
            
            logger.info(f"VNC 输入成功: {vm_name}")

        except asyncio.TimeoutError:
            raise Exception(f"连接 VNC 超时: {vm_name}")
        except Exception as e:
            logger.error(f"VNC 输入失败: {e}")
            raise Exception(f"输入失败: {str(e)}")

    async def press_key(self, vm_name: str, key: str) -> None:
        """
        按下特殊按键

        Args:
            vm_name: 虚拟机名称
            key: 按键名称 (enter/esc/tab/backspace/delete/up/down/left/right/f1-f12等)

        Raises:
            Exception: 操作失败
        """
        try:
            from vncdotool import api
        except ImportError:
            raise Exception("vncdotool 库未安装，请运行: pip install vncdotool")

        try:
            host, port = await self._get_vnc_connection_info(vm_name)
            
            logger.info(f"VNC 按键: {vm_name} key={key}")

            # 连接 VNC
            client = await asyncio.wait_for(
                asyncio.to_thread(api.connect, f"{host}::{port}"),
                timeout=10.0
            )

            # 按键映射（vncdotool 使用的按键名称）
            key_map = {
                "enter": "return",
                "esc": "escape",
                "backspace": "bsp",
                "delete": "del",
                "up": "up",
                "down": "down",
                "left": "left",
                "right": "right",
                "tab": "tab",
                "space": "space",
                "ctrl": "ctrl",
                "alt": "alt",
                "shift": "shift",
            }
            
            # 转换按键名称
            vnc_key = key_map.get(key.lower(), key.lower())
            
            # 按下按键
            await asyncio.to_thread(client.keyPress, vnc_key)
            
            logger.info(f"VNC 按键成功: {vm_name}")

        except asyncio.TimeoutError:
            raise Exception(f"连接 VNC 超时: {vm_name}")
        except Exception as e:
            logger.error(f"VNC 按键失败: {e}")
            raise Exception(f"按键失败: {str(e)}")

    async def mouse_move(self, vm_name: str, x: int, y: int) -> None:
        """
        移动鼠标到指定位置

        Args:
            vm_name: 虚拟机名称
            x: 横坐标
            y: 纵坐标

        Raises:
            Exception: 操作失败
        """
        try:
            from vncdotool import api
        except ImportError:
            raise Exception("vncdotool 库未安装，请运行: pip install vncdotool")

        try:
            host, port = await self._get_vnc_connection_info(vm_name)
            
            logger.info(f"VNC 鼠标移动: {vm_name} ({x}, {y})")

            # 连接 VNC
            client = await asyncio.wait_for(
                asyncio.to_thread(api.connect, f"{host}::{port}"),
                timeout=10.0
            )

            # 移动鼠标
            await asyncio.to_thread(client.mouseMove, x, y)
            
            logger.info(f"VNC 鼠标移动成功: {vm_name}")

        except asyncio.TimeoutError:
            raise Exception(f"连接 VNC 超时: {vm_name}")
        except Exception as e:
            logger.error(f"VNC 鼠标移动失败: {e}")
            raise Exception(f"鼠标移动失败: {str(e)}")
