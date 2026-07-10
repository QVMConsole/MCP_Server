# QVMConsole MCP - VNC 控制功能使用指南

## 📖 简介

QVMConsole MCP Server 实现了基于 VNC 协议的虚拟机远程控制功能，允许 AI 模型通过截图、鼠标、键盘操作直接控制虚拟机界面。这是一种类似 Anthropic Computer Use 的实现方案。

## 🏗️ 架构设计

### 技术方案

采用 **截图式操控** 方案（方案一）：

```
┌─────────────────────────────────────────────┐
│           AI 模型 (Claude/GPT-4V)           │
└──────────────────┬──────────────────────────┘
                   │ MCP 协议
┌──────────────────▼──────────────────────────┐
│      MCP Server (VNC 控制工具)               │
│  工具:                                        │
│  - vnc_screenshot: 截图                      │
│  - vnc_click: 鼠标点击                       │
│  - vnc_type: 键盘输入                        │
│  - vnc_key: 特殊按键                         │
│  - vnc_move: 鼠标移动                        │
└──────────────────┬──────────────────────────┘
                   │ Python vncdotool
┌──────────────────▼──────────────────────────┐
│   QVMConsole API (获取 VNC 连接信息)         │
│   GET /api/vm/:name/vnc/status              │
└──────────────────┬──────────────────────────┘
                   │ TCP 127.0.0.1:port
┌──────────────────▼──────────────────────────┐
│         VNC Server (VM 虚拟机)               │
└─────────────────────────────────────────────┘
```

### 核心组件

1. **vnc_controller.py** - VNC 控制器
   - 连接管理
   - 截图功能
   - 鼠标键盘操作

2. **client.py** - API 客户端扩展
   - `get_vnc_status()` - 获取 VNC 状态
   - `enable_vnc()` - 开启 VNC

3. **tools.py** - MCP 工具集
   - 7 个 VNC 相关工具
   - 统一的错误处理

## 🚀 快速开始

### 1. 安装依赖

```bash
cd "c:\Users\17737\Code\Opensource\QVMConsole\Code\MCP Server"

# 激活虚拟环境（如果使用）
.\venv\Scripts\Activate

# 安装 VNC 依赖
pip install vncdotool Pillow
```

### 2. 开启虚拟机 VNC

在 Claude Desktop 中：

```
请为虚拟机 test-vm 开启 VNC
```

AI 会调用：
```python
vnc_enable(vm_name="test-vm", password="vnc123")
```

### 3. 截取屏幕画面

```
截取 test-vm 的屏幕画面
```

AI 会调用：
```python
vnc_screenshot(vm_name="test-vm")
```

**返回**: PNG 图片（自动显示在对话中）

### 4. 操控虚拟机

```
在屏幕坐标 (500, 300) 点击鼠标左键
```

```
输入文本 "hello world"
```

```
按下回车键
```

## 📋 可用工具列表

### 1. vnc_status - 查看 VNC 状态

**功能**: 查看虚拟机 VNC 是否已启用及连接信息

**参数**:
- `vm_name` (必填) - 虚拟机名称

**返回信息**:
- VNC 启用状态
- 监听端口
- 认证方式
- 是否对外暴露

**示例**:
```python
vnc_status(vm_name="ubuntu-vm")
```

---

### 2. vnc_enable - 开启 VNC

**功能**: 为虚拟机开启 VNC 服务

**参数**:
- `vm_name` (必填) - 虚拟机名称
- `password` (可选) - VNC 密码，不填则无密码

**注意**:
- 虚拟机必须处于运行状态
- 开启 VNC 会重启虚拟机（如果正在运行）

**示例**:
```python
vnc_enable(vm_name="ubuntu-vm", password="secure123")
```

---

### 3. vnc_screenshot - 截取画面

**功能**: 截取虚拟机当前屏幕画面

**参数**:
- `vm_name` (必填) - 虚拟机名称

**返回**: base64 编码的 PNG 图像

**用途**:
- 查看虚拟机当前状态
- 定位界面元素坐标
- 确认操作结果

**示例**:
```python
vnc_screenshot(vm_name="ubuntu-vm")
```

---

### 4. vnc_click - 鼠标点击

**功能**: 在指定坐标点击鼠标

**参数**:
- `vm_name` (必填) - 虚拟机名称
- `x` (必填) - 横坐标（像素）
- `y` (必填) - 纵坐标（像素）
- `button` (可选) - 鼠标按键，默认 `left`
  - `left` - 左键
  - `right` - 右键
  - `middle` - 中键

**坐标说明**:
- 原点 (0, 0) 在屏幕左上角
- 需要先截图确定元素位置

**示例**:
```python
# 左键点击
vnc_click(vm_name="ubuntu-vm", x=500, y=300)

# 右键点击
vnc_click(vm_name="ubuntu-vm", x=640, y=480, button="right")
```

---

### 5. vnc_type - 输入文本

**功能**: 在虚拟机中输入文本

**参数**:
- `vm_name` (必填) - 虚拟机名称
- `text` (必填) - 要输入的文本内容

**支持**:
- 英文字母、数字
- 常见符号
- 空格

**限制**:
- 不支持中文输入（VNC 协议限制）
- 特殊字符可能需要按键组合

**示例**:
```python
vnc_type(vm_name="ubuntu-vm", text="ls -la")
```

---

### 6. vnc_key - 特殊按键

**功能**: 按下特殊功能按键

**参数**:
- `vm_name` (必填) - 虚拟机名称
- `key` (必填) - 按键名称

**支持的按键**:

| 按键名称 | 说明 | 用途 |
|---------|------|------|
| `enter` | 回车键 | 提交、确认 |
| `esc` | 退出键 | 取消、退出 |
| `tab` | 制表键 | 切换焦点 |
| `backspace` | 退格键 | 删除前一个字符 |
| `delete` | 删除键 | 删除当前字符 |
| `up` | 上方向键 | 向上移动 |
| `down` | 下方向键 | 向下移动 |
| `left` | 左方向键 | 向左移动 |
| `right` | 右方向键 | 向右移动 |
| `space` | 空格键 | 空格 |
| `ctrl` | Ctrl 键 | 组合键 |
| `alt` | Alt 键 | 组合键 |
| `shift` | Shift 键 | 组合键 |
| `f1-f12` | 功能键 | 特殊功能 |

**示例**:
```python
# 按下回车
vnc_key(vm_name="ubuntu-vm", key="enter")

# 按下 ESC
vnc_key(vm_name="ubuntu-vm", key="esc")

# 按下方向键
vnc_key(vm_name="ubuntu-vm", key="down")
```

---

### 7. vnc_move - 移动鼠标

**功能**: 移动鼠标到指定位置（不点击）

**参数**:
- `vm_name` (必填) - 虚拟机名称
- `x` (必填) - 横坐标（像素）
- `y` (必填) - 纵坐标（像素）

**用途**:
- 悬停查看提示
- 准备点击操作

**示例**:
```python
vnc_move(vm_name="ubuntu-vm", x=800, y=400)
```

---

## 💡 使用场景示例

### 场景 1：查看虚拟机桌面

**目标**: 查看虚拟机当前显示内容

**步骤**:
1. 检查 VNC 状态
2. 如果未开启则开启 VNC
3. 截取屏幕画面

**AI 对话示例**:
```
用户: 查看一下 ubuntu-vm 的桌面

AI: 
【步骤 1】检查 VNC 状态
[调用 vnc_status]
VNC 已启用 ✅

【步骤 2】截取屏幕画面
[调用 vnc_screenshot]

✅ 已截取屏幕画面：
[显示图片]

当前虚拟机显示登录界面。
```

---

### 场景 2：登录虚拟机

**目标**: 通过 VNC 在图形界面登录

**步骤**:
1. 截图查看当前状态
2. 点击用户名输入框
3. 输入用户名
4. 按 Tab 切换到密码框
5. 输入密码
6. 按回车登录
7. 截图确认登录成功

**AI 对话示例**:
```
用户: 帮我通过 VNC 登录 ubuntu-vm

AI:
【步骤 1】截取当前画面
[vnc_screenshot]
看到登录界面，用户名框在坐标 (500, 300)

【步骤 2】点击用户名框
[vnc_click(x=500, y=300)]
✅ 已点击

【步骤 3】输入用户名
[vnc_type(text="ubuntu")]
✅ 已输入用户名

【步骤 4】切换到密码框
[vnc_key(key="tab")]
✅ 已切换

【步骤 5】输入密码
[vnc_type(text="Pass123")]
✅ 已输入密码

【步骤 6】提交登录
[vnc_key(key="enter")]
✅ 已提交

【步骤 7】等待并确认
[等待 3 秒]
[vnc_screenshot]

✅ 登录成功！已进入桌面。
```

---

### 场景 3：打开终端并执行命令

**目标**: 在桌面环境中打开终端并运行命令

**步骤**:
1. 截图查看桌面
2. 右键点击桌面
3. 截图查看右键菜单
4. 点击"Open Terminal"
5. 截图确认终端打开
6. 输入命令
7. 按回车执行

**AI 对话示例**:
```
用户: 在虚拟机桌面上打开终端并执行 ls 命令

AI:
【步骤 1】查看桌面
[vnc_screenshot]
看到 Ubuntu 桌面

【步骤 2】右键点击桌面
[vnc_click(x=640, y=400, button="right")]
✅ 已右键点击

【步骤 3】查看菜单
[vnc_screenshot]
"Open Terminal" 在 (660, 480)

【步骤 4】点击打开终端
[vnc_click(x=660, y=480)]
✅ 终端已打开

【步骤 5】确认终端
[vnc_screenshot]
✅ 终端窗口已显示

【步骤 6】输入命令
[vnc_type(text="ls -la")]
✅ 已输入命令

【步骤 7】执行命令
[vnc_key(key="enter")]
✅ 命令已执行

【步骤 8】查看结果
[vnc_screenshot]
✅ 命令执行成功，显示文件列表。
```

---

## ⚠️ 注意事项

### 1. 前置条件

**必须满足**:
- ✅ 虚拟机处于运行状态
- ✅ VNC 已开启（使用 `vnc_enable`）
- ✅ MCP Server 运行在 QVMConsole 宿主机上

**检查方法**:
```python
# 1. 检查虚拟机状态
get_vm_info(vm_name="xxx")

# 2. 检查 VNC 状态
vnc_status(vm_name="xxx")
```

---

### 2. 坐标定位技巧

**坐标系统**:
- 原点 (0, 0) 在屏幕左上角
- X 轴向右递增
- Y 轴向下递增

**定位流程**:
1. 先截图查看界面
2. 根据截图估算元素位置
3. 点击后截图确认
4. 如果位置不准确，调整坐标重试

**常见元素位置**:
- 屏幕中央: (width/2, height/2)
- 左上角菜单: (50, 50)
- 右下角图标: (width-50, height-50)

---

### 3. 操作间隔建议

**为什么需要等待**:
- VNC 操作有网络延迟
- 虚拟机界面响应需要时间
- 过快操作可能导致漏失

**建议间隔**:
- 截图后: 无需等待
- 点击后: 等待 0.5 秒
- 输入后: 等待 0.5 秒
- 按键后: 等待 0.5 秒
- 复杂操作: 等待 1-2 秒并截图确认

**示例**:
```python
# 点击
vnc_click(x=500, y=300)
# 等待 0.5 秒
time.sleep(0.5)
# 截图确认
vnc_screenshot()
```

---

### 4. 性能考虑

**截图开销**:
- 单次截图: 1-2 秒
- 图像大小: 50KB - 500KB
- 网络传输: 视网络而定

**优化建议**:
- ❌ 避免高频连续截图
- ✅ 仅在需要确认时截图
- ✅ 批量操作后再截图

**不好的做法**:
```python
# ❌ 每次操作都截图
for i in range(10):
    vnc_click(x, y)
    vnc_screenshot()  # 太频繁
```

**好的做法**:
```python
# ✅ 批量操作后截图
for i in range(10):
    vnc_click(x, y)
    time.sleep(0.5)
vnc_screenshot()  # 一次确认
```

---

### 5. 安全注意事项

**VNC 安全**:
- 🔒 VNC 默认监听 `127.0.0.1`（本地访问）
- 🔑 建议设置 VNC 密码
- ⚠️ 不要对外暴露 VNC 端口

**密码保护**:
```python
# 推荐：设置密码
vnc_enable(vm_name="xxx", password="Secure@123")

# 不推荐：无密码
vnc_enable(vm_name="xxx")
```

**访问控制**:
- MCP Server 必须与 QVMConsole 在同一宿主机
- VNC 不支持远程访问（仅本地 127.0.0.1）
- 如需远程，使用 SSH 隧道

---

## 🐛 故障排除

### 问题 1: "VNC 未开启"

**错误信息**:
```
❌ VNC 截图失败: 虚拟机 xxx 的 VNC 未开启，请先开启 VNC
```

**原因**: VNC 服务未启动

**解决方法**:
```python
# 开启 VNC
vnc_enable(vm_name="xxx")

# 等待 5 秒
time.sleep(5)

# 再次尝试截图
vnc_screenshot(vm_name="xxx")
```

---

### 问题 2: "连接 VNC 超时"

**错误信息**:
```
❌ 连接 VNC 超时: xxx
```

**可能原因**:
1. 虚拟机未运行
2. VNC 服务未完全启动
3. 网络连接问题
4. MCP Server 不在同一宿主机

**排查步骤**:
```python
# 1. 检查虚拟机状态
get_vm_info(vm_name="xxx")
# 确认 status: running

# 2. 检查 VNC 状态
vnc_status(vm_name="xxx")
# 确认 enabled: true

# 3. 等待一段时间后重试
time.sleep(5)
vnc_screenshot(vm_name="xxx")
```

---

### 问题 3: "vncdotool 库未安装"

**错误信息**:
```
❌ vncdotool 库未安装，请运行: pip install vncdotool
```

**解决方法**:
```bash
# 激活虚拟环境
.\venv\Scripts\Activate

# 安装依赖
pip install vncdotool Pillow
```

---

### 问题 4: 点击位置不准确

**现象**: 点击后没有触发预期效果

**原因**: 坐标估算不准确

**解决方法**:
1. 先截图查看
2. 使用图片查看工具标记坐标
3. 调整坐标重试
4. 截图确认结果

**技巧**: 
- 可以先点击一个安全位置测试
- 逐步接近目标位置
- 使用 `vnc_move` 先移动再点击

---

### 问题 5: 输入的文本不显示

**可能原因**:
1. 输入焦点不在输入框
2. 输入速度过快
3. 虚拟机响应慢

**解决方法**:
```python
# 1. 先点击输入框获取焦点
vnc_click(x=500, y=300)
time.sleep(0.5)

# 2. 再输入文本
vnc_type(text="hello")
time.sleep(0.5)

# 3. 截图确认
vnc_screenshot()
```

---

## 📊 功能限制

| 功能 | 支持情况 | 说明 |
|------|---------|------|
| 截图 | ✅ 完全支持 | PNG 格式，自动显示 |
| 鼠标点击 | ✅ 完全支持 | 左键/右键/中键 |
| 鼠标移动 | ✅ 完全支持 | 精确定位 |
| 键盘输入 | ✅ 支持 | 仅英文和符号 |
| 特殊按键 | ✅ 支持 | 常用功能键 |
| 鼠标拖拽 | ⚠️ 部分支持 | 需组合移动+点击 |
| 中文输入 | ❌ 不支持 | VNC 协议限制 |
| 剪贴板 | ❌ 不支持 | VNC 协议限制 |
| 文件传输 | ❌ 不支持 | 建议使用 SSH |
| 实时视频 | ❌ 不支持 | 仅支持截图模式 |

---

## 🔗 相关资源

- **MCP 协议文档**: https://modelcontextprotocol.io/
- **vncdotool 文档**: https://github.com/sibson/vncdotool
- **QVMConsole 文档**: https://qvmcdocs.xiaozhuhouses.asia/
- **Anthropic Computer Use**: https://docs.anthropic.com/en/docs/agents/computer-use

---

## 📝 更新日志

### v0.2.0 (2026-07-10)
- ✨ 新增 VNC 控制功能
- ✨ 新增 7 个 VNC 工具
- ✨ 支持截图、点击、输入操作
- 📚 完善 VNC 使用文档

---

**创建日期**: 2026-07-10  
**作者**: QVMConsole MCP Team  
**版本**: v0.2.0
