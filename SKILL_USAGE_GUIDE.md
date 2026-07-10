# QVMConsole MCP Skill 使用指南

## 📌 快速开始

### 给 AI 模型的指令

当你需要使用 QVMConsole MCP 管理虚拟机时，请参考这个 Skill 文件：

```
请使用 qvmconsole-vm-management skill 来帮我创建虚拟机
```

## 🎯 完整开发测试流程

### 标准流程（必须按此顺序执行）

#### 1️⃣ 获取所有可用模板
```
请列出所有可用的虚拟机模板
```

**AI 会调用**: `list_templates`

**预期输出**: 模板列表，包括名称、类型、状态

---

#### 2️⃣ 创建虚拟机（重要：必须包含必需参数）

```
使用 Ubuntu26.04-LTS 模板创建一个虚拟机，配置 2 核 CPU 和 4GB 内存
```

**AI 必须提供的参数**:
- ✅ `template_name`: 模板名称
- ✅ `vm_name`: 虚拟机名称
- ✅ `vcpu`: CPU 核心数
- ✅ `ram`: 内存大小
- ✅ `user`: 用户名（Linux 模板必需）
- ✅ `password`: 密码（Linux 模板必需）

**示例调用**:
```python
create_vm_from_template(
    template_name="Ubuntu26.04-LTS",
    vm_name="test-ubuntu-vm",
    vcpu=2,
    ram=4,
    user="ubuntu",
    password="SecurePass123"
)
```

**预期输出**: 任务 ID

---

#### 3️⃣ 等待虚拟机创建完成

**关键**: 必须等待 **20 秒**，让虚拟机完成初始化

```
等待 20 秒...
```

---

#### 4️⃣ 获取虚拟机信息（包含账号密码）

```
查看虚拟机的详细信息和登录凭据
```

**AI 会调用**: `get_vm_info`

**预期输出**:
- IP 地址
- 用户名
- 密码
- 状态
- 配置信息

---

#### 5️⃣ 使用 SSH 连接测试

AI 应该提供 SSH 连接命令：

```
SSH 连接命令：
ssh ubuntu@192.168.1.100

密码：SecurePass123
```

如果有 SSH MCP 工具，可以直接测试连接：

```
让我测试 SSH 连接...

[使用 SSH MCP 连接]
[执行命令: uname -a]
[执行命令: free -h]
[执行命令: df -h]

✅ SSH 连接测试成功！
```

---

## ⚠️ 关键注意事项

### 1. Linux 模板必需参数

**错误示例** ❌:
```python
# 缺少 user 和 password
create_vm_from_template(
    template_name="Ubuntu26.04-LTS",
    vm_name="test-vm",
    vcpu=2,
    ram=4
)
# 结果：API 返回 "请输入用户名"
```

**正确示例** ✅:
```python
# 包含所有必需参数
create_vm_from_template(
    template_name="Ubuntu26.04-LTS",
    vm_name="test-vm",
    vcpu=2,
    ram=4,
    user="ubuntu",        # 必需
    password="Pass123"    # 必需
)
```

### 2. 常见用户名

| 模板类型 | 默认用户名 |
|---------|-----------|
| Ubuntu | ubuntu |
| Debian | debian |
| CentOS/RHEL | root 或 centos |
| Generic Linux | root |

### 3. 密码要求

- 长度：至少 8 位
- 复杂度：建议包含大小写字母、数字
- 安全性：不要使用 "123456"、"password" 等常见密码

### 4. 等待时间

- **创建后必须等待**: 20 秒
- **原因**: 虚拟机需要时间启动并获取 IP 地址
- **不等待的后果**: 获取不到 IP 地址和完整信息

---

## 📋 完整示例对话

### 示例：创建并测试 Ubuntu 虚拟机

**用户**: 帮我创建一个 Ubuntu 虚拟机用于测试

**AI 响应流程**:

```markdown
好的，我来帮你创建一个 Ubuntu 虚拟机。

【步骤 1】首先查看可用模板
[调用 list_templates]

找到可用模板：Ubuntu26.04-LTS ✅

【步骤 2】创建虚拟机
配置信息：
- 模板：Ubuntu26.04-LTS
- 名称：ubuntu-test-vm
- CPU：2 核
- 内存：4 GB
- 用户名：ubuntu
- 密码：Test@2024Secure

[调用 create_vm_from_template 并传入所有必需参数]

✅ 虚拟机创建任务已提交
任务 ID: 123

【步骤 3】等待虚拟机初始化
正在等待虚拟机启动...（约需 20 秒）
[等待 20 秒]

【步骤 4】获取虚拟机信息
[调用 get_vm_info]

✅ 虚拟机已创建并启动成功！

📋 虚拟机信息：
- 名称：ubuntu-test-vm
- IP 地址：192.168.1.100
- 状态：running
- CPU：2 核
- 内存：4 GB

🔐 登录凭据：
- 用户名：ubuntu
- 密码：Test@2024Secure

【步骤 5】SSH 连接命令
ssh ubuntu@192.168.1.100

密码：Test@2024Secure

【步骤 6】测试连接（如果有 SSH MCP）
[使用 SSH MCP 连接虚拟机]
[执行: uname -a]
[执行: free -h]

✅ SSH 连接测试成功！虚拟机运行正常。
```

---

## 🔧 故障排除

### 问题 1: "请输入用户名"

**原因**: 缺少 `user` 参数

**解决**: 添加 `user` 和 `password` 参数

```python
# 添加这两个参数
user="ubuntu"
password="YourPassword123"
```

---

### 问题 2: "磁盘空间不足"

**解决流程**:

1. 检查存储池
```
[调用 list_storage_pools]
```

2. 选择有空间的存储池
```python
create_vm_from_template(
    # ... 其他参数
    storage_pool_id="pool-with-space"  # 添加此参数
)
```

---

### 问题 3: 无法获取 IP 地址

**原因**: 没有等待足够时间

**解决**: 创建后等待 20 秒再查询虚拟机信息

---

## 🖥️ VNC 操作功能

### VNC 功能概述

QVMConsole MCP 支持通过 VNC 远程查看和操控虚拟机画面，实现 AI 模型直接操控虚拟机的能力。

### VNC 操作流程

#### 1️⃣ 查看 VNC 状态

```
查看虚拟机的 VNC 状态
```

**AI 会调用**: `vnc_status`

**预期输出**: VNC 是否已启用、端口、认证方式等

---

#### 2️⃣ 开启 VNC（如果未启用）

```
为虚拟机开启 VNC
```

**AI 会调用**: `vnc_enable`

**可选参数**:
- `password`: VNC 密码（可选，不填则无密码）

**示例调用**:
```python
vnc_enable(
    vm_name="test-ubuntu-vm",
    password="vnc123"  # 可选
)
```

---

#### 3️⃣ 截取 VNC 画面

```
截取虚拟机的屏幕画面
```

**AI 会调用**: `vnc_screenshot`

**预期输出**: 虚拟机当前屏幕的截图（PNG 格式）

**注意**: 
- 虚拟机必须处于运行状态
- VNC 必须已开启
- 截图会自动显示在对话中

---

#### 4️⃣ VNC 交互操作

##### 点击操作
```
在坐标 (500, 300) 点击鼠标左键
```

**AI 会调用**: `vnc_click`

**参数**:
- `x`: 横坐标（像素）
- `y`: 纵坐标（像素）
- `button`: 鼠标按键（left/right/middle）

##### 输入文本
```
在虚拟机中输入 "hello world"
```

**AI 会调用**: `vnc_type`

##### 按下特殊按键
```
按下回车键
```

**AI 会调用**: `vnc_key`

**支持的按键**:
- `enter` - 回车
- `esc` - 退出键
- `tab` - 制表键
- `backspace` - 退格
- `delete` - 删除
- `up/down/left/right` - 方向键
- `space` - 空格
- `ctrl/alt/shift` - 功能键
- `f1-f12` - 功能键

##### 移动鼠标
```
移动鼠标到坐标 (800, 400)
```

**AI 会调用**: `vnc_move`

---

### VNC 操作示例

#### 示例 1：查看虚拟机屏幕

**用户**: 查看一下虚拟机的桌面画面

**AI 响应流程**:
```markdown
【步骤 1】检查 VNC 状态
[调用 vnc_status]

VNC 状态：已启用 ✅
端口：5900
认证：无需密码

【步骤 2】截取屏幕画面
[调用 vnc_screenshot]

✅ 已截取虚拟机屏幕画面：

[显示截图]

当前看到虚拟机正在显示登录界面。
```

---

#### 示例 2：通过 VNC 登录虚拟机

**用户**: 帮我通过 VNC 登录虚拟机

**AI 响应流程**:
```markdown
【步骤 1】截取当前画面
[调用 vnc_screenshot]

看到登录界面，用户名输入框在屏幕中央位置。

【步骤 2】点击用户名输入框
[调用 vnc_click(x=500, y=300)]

✅ 已点击用户名输入框

【步骤 3】输入用户名
[调用 vnc_type(text="ubuntu")]

✅ 已输入用户名

【步骤 4】按下 Tab 键切换到密码框
[调用 vnc_key(key="tab")]

✅ 已切换到密码框

【步骤 5】输入密码
[调用 vnc_type(text="YourPassword")]

✅ 已输入密码

【步骤 6】按下回车登录
[调用 vnc_key(key="enter")]

✅ 已提交登录

【步骤 7】等待并确认登录成功
[等待 3 秒]
[调用 vnc_screenshot]

✅ 登录成功！现在已进入桌面环境。
```

---

#### 示例 3：在虚拟机中执行操作

**用户**: 帮我在虚拟机桌面上打开终端

**AI 响应流程**:
```markdown
【步骤 1】截取当前画面
[调用 vnc_screenshot]

看到 Ubuntu 桌面，左下角有应用程序菜单。

【步骤 2】右键点击桌面
[调用 vnc_click(x=640, y=400, button="right")]

✅ 已右键点击

【步骤 3】截图查看菜单
[调用 vnc_screenshot]

看到右键菜单，"Open Terminal" 选项在 (660, 480) 位置。

【步骤 4】点击打开终端
[调用 vnc_click(x=660, y=480)]

✅ 终端已打开

【步骤 5】确认终端打开
[调用 vnc_screenshot]

✅ 终端窗口已成功打开！
```

---

### VNC 操作注意事项

#### 1. 前置条件
- ✅ 虚拟机必须处于运行状态
- ✅ VNC 必须已开启（使用 `vnc_enable`）
- ✅ MCP Server 必须运行在与 QVMConsole 相同的宿主机上

#### 2. 坐标定位
- 坐标原点 (0, 0) 在屏幕左上角
- 需要根据截图确定元素位置
- 不同分辨率的虚拟机坐标不同

#### 3. 操作间隔
- 建议在操作之间等待 0.5-1 秒
- 复杂操作（如登录）建议截图确认状态
- 输入文本后建议截图确认输入成功

#### 4. 性能考虑
- 截图操作有一定延迟（1-2 秒）
- 不建议连续高频截图
- 每次操作后截图确认即可

#### 5. 安全注意
- VNC 默认仅监听 127.0.0.1（本地访问）
- 建议设置 VNC 密码保护
- 不要在公网暴露 VNC 端口

---

### VNC 功能限制

| 功能 | 是否支持 | 说明 |
|------|---------|------|
| 截图 | ✅ 支持 | PNG 格式，自动显示 |
| 鼠标点击 | ✅ 支持 | 左键/右键/中键 |
| 键盘输入 | ✅ 支持 | 文本和特殊按键 |
| 鼠标拖拽 | ⚠️ 部分支持 | 需要组合移动和点击操作 |
| 剪贴板 | ❌ 不支持 | VNC 协议限制 |
| 文件传输 | ❌ 不支持 | 建议使用 SSH |
| 实时视频 | ❌ 不支持 | 仅支持截图模式 |

---

### 故障排除

#### 问题 1: "VNC 未开启"

**解决**:
```
[调用 vnc_enable(vm_name="xxx")]
```

---

#### 问题 2: "连接 VNC 超时"

**原因**: 
- 虚拟机未运行
- 网络连接问题
- MCP Server 不在同一宿主机

**解决**: 
1. 检查虚拟机状态
2. 确认 MCP Server 位置
3. 查看日志文件

---

#### 问题 3: "截图失败"

**可能原因**:
- vncdotool 库未安装
- VNC 端口冲突
- 虚拟机图形界面未启动

**解决**:
```bash
# 安装依赖
pip install vncdotool Pillow

# 检查 VNC 状态
[调用 vnc_status]
```

---

## 📚 相关文档

- 完整 Skill 定义: [qvmconsole-vm-management.skill.md](qvmconsole-vm-management.skill.md)
- 使用文档: [docs/usage.md](docs/usage.md)
- 存储池功能: [STORAGE_POOL_FEATURE.md](STORAGE_POOL_FEATURE.md)

---

## ✅ 检查清单

在创建虚拟机前，确保：

- [ ] 已调用 `list_templates` 查看可用模板
- [ ] 选择了合适的模板
- [ ] 提供了 `user` 参数（Linux 模板）
- [ ] 提供了 `password` 参数（Linux 模板）
- [ ] 虚拟机名称是唯一的
- [ ] 创建后等待 20 秒
- [ ] 调用 `get_vm_info` 获取完整信息
- [ ] 提供了 SSH 连接命令
- [ ] （可选）测试了 SSH 连接

---

**创建日期**: 2026-07-10  
**适用版本**: QVMConsole MCP Server 0.1.0+
