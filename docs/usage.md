# QVMConsole MCP Server 使用文档

## 快速开始

### 1. 安装配置

参考 [README.md](../README.md) 完成安装和配置。

### 2. 获取 API Key

1. 登录 QVMConsole Web 管理面板
2. 点击右上角用户名，进入 **个人中心**
3. 在左侧菜单选择 **API Key 管理**
4. 点击 **生成 API Key** 按钮
5. 完成二次验证（如果启用了）
6. **立即复制并保存** API Key ID 和 API Key（只显示一次）

**示例：**
- API Key ID: `kvm_id_AbC123XyZ456789012`
- API Key: `kvm_sk_AbC123XyZ456789012345678901234567890123456`

### 3. 配置文件

编辑 `config/config.json`：

```json
{
  "qvmconsole": {
    "base_url": "http://your-server:8082",
    "api_key_id": "kvm_id_AbC123XyZ456789012",
    "api_key": "kvm_sk_AbC123XyZ456789012345678901234567890123456",
    "timeout": 30,
    "verify_ssl": true
  },
  "mcp": {
    "server_name": "qvmconsole-mcp-server",
    "version": "0.1.0"
  },
  "logging": {
    "level": "INFO",
    "file": "logs/mcp-server.log"
  }
}
```

**配置说明：**
- `base_url`: QVMConsole 服务器地址（不要忘记端口号）
- `api_key_id`: API Key ID（以 `kvm_id_` 开头）
- `api_key`: API Key（以 `kvm_sk_` 开头）
- `timeout`: 请求超时时间（秒）
- `verify_ssl`: 是否验证 SSL 证书（HTTPS 时需要）

## 命令行测试

在集成到 Claude Desktop 之前，可以先用命令行脚本测试连接。

### 方式 1：简单测试脚本

```bash
# 激活虚拟环境
source venv/Scripts/activate  # Windows
source venv/bin/activate      # Linux/Mac

# 运行测试脚本列出虚拟机
python test_list_vms.py
```

输出示例：
```
VM List (Total: 1):

1. [RUN] vmob8wrys7
   State: running
   CPU/RAM: 2 cores / 2.0 GB
   IP: 192.168.11.100
```

### 方式 2：交互式客户端

```bash
python interactive_client.py
```

菜单选项：
1. List all VMs - 列出虚拟机
2. List templates - 列出模板
3. Get VM info - 获取虚拟机详情
4. Exit - 退出

### 方式 3：直接启动 MCP 服务器

```bash
python src/server.py
```

这会启动 MCP 服务器，可以通过 Claude Desktop 连接。

## 在 Claude Desktop 中使用

### 配置 Claude Desktop

**macOS**:
```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows**:
```
记事本打开 %APPDATA%\Claude\claude_desktop_config.json
```

添加配置：

```json
{
  "mcpServers": {
    "qvmconsole": {
      "command": "python",
      "args": [
        "C:\\Users\\YourName\\QVMConsole-MCP-Server\\src\\server.py"
      ]
    }
  }
}
```

**注意：**
- Windows 路径使用双反斜杠 `\\` 或单斜杠 `/`
- macOS/Linux 使用完整路径，如 `/home/user/QVMConsole-MCP-Server/src/server.py`

### 重启 Claude Desktop

配置完成后，完全退出并重启 Claude Desktop。

### 验证连接

在 Claude Desktop 对话框中输入：

```
请列出所有可用的虚拟机模板
```

如果返回模板列表，说明配置成功！

## 使用示例

### 查看模板

**提问：**
> 列出所有可用的虚拟机模板

**回复示例：**
```
可用的虚拟机模板列表:

1. **Ubuntu 22.04 LTS** (ubuntu-22.04)
   - 类型: linux
   - 分类: Ubuntu
   - 状态: ✅ 可用

2. **Debian 12** (debian-12)
   - 类型: linux
   - 分类: Debian
   - 状态: ✅ 可用
```

### 创建虚拟机

**提问：**
> 使用 ubuntu-22.04 模板创建一个虚拟机，名称为 test-server，配置为 2核4G，磁盘 50GB，密码设置为 MyPassword123

**回复示例：**
```
✅ 虚拟机创建任务已提交

- 虚拟机名称: test-server
- 使用模板: ubuntu-22.04
- CPU: 2 核心
- 内存: 4 GB
- 磁盘: 50 GB

任务 ID: 12345

提示: 使用 get_vm_info 查看虚拟机详情和密码
```

### 查看虚拟机信息（含密码）

**提问：**
> 查看 test-server 的详细信息，包括登录密码

**回复示例：**
```
虚拟机详细信息: **test-server**

## 基本信息
- 名称: test-server
- 状态: running
- UUID: 12345678-1234-1234-1234-123456789abc

## 硬件配置
- CPU: 2 核心
- 内存: 4096 MB

## 网络信息
- IP 地址: 192.168.122.10
- MAC 地址: 52:54:00:12:34:56

## 🔑 登录信息
- 用户名: `root`
- 密码: `MyPassword123`

## 运行状态
- 自动启动: 否
- 运行时间: 00:05:23
```

### 列出所有虚拟机

**提问：**
> 列出所有虚拟机

**回复示例：**
```
虚拟机列表 (共 3 台):

1. 🟢 **test-server**
   - 状态: running
   - 配置: 2 核 / 4.0 GB
   - IP: 192.168.122.10

2. 🔴 **dev-vm**
   - 状态: shut off
   - 配置: 4 核 / 8.0 GB
   - IP: 无

3. 🟢 **web-server**
   - 状态: running
   - 配置: 2 核 / 2.0 GB
   - IP: 192.168.122.15
```

### 编辑虚拟机

**提问：**
> 将 test-server 的内存调整为 8GB，CPU 调整为 4核

**回复示例：**
```
✅ 虚拟机配置已更新: test-server

修改内容:
- CPU: 4 核心
- 内存: 8 GB
```

## 更多用法

### 批量操作

**提问：**
> 我需要创建 3 台测试虚拟机，配置都是 2核4G，名称分别为 test-01、test-02、test-03

Claude 会调用三次 `create_vm_from_template` 工具完成批量创建。

### 复杂查询

**提问：**
> 列出所有正在运行的虚拟机，并告诉我它们的 IP 地址和登录密码

Claude 会先调用 `list_vms` 获取列表，然后对每台运行中的虚拟机调用 `get_vm_info` 获取详细信息。

## 故障排查

### 问题 1: "配置文件不存在"

**错误信息：**
```
配置文件不存在: config/config.json
```

**解决方法：**
1. 确保已复制 `config.example.json` 为 `config.json`
2. 确认文件路径正确

### 问题 2: "API 凭证无效"

**错误信息：**
```
❌ API 凭证无效
```

**解决方法：**
1. 检查 `api_key_id` 和 `api_key` 是否正确复制
2. 确认 API Key 未被撤销（在 QVMConsole 管理面板查看）
3. 确认用户账号未被禁用

### 问题 3: "请求超时"

**错误信息：**
```
❌ 请求超时: http://...
```

**解决方法：**
1. 检查 `base_url` 是否正确
2. 确认 QVMConsole 服务正在运行
3. 检查网络连接和防火墙设置
4. 增加 `timeout` 配置值

### 问题 4: Claude Desktop 无法连接

**现象：**
工具调用失败或没有反应

**解决方法：**
1. 检查 Claude Desktop 配置文件路径是否正确
2. 确认 Python 路径正确（运行 `which python` 或 `where python`）
3. 查看日志文件 `logs/mcp-server.log`
4. 完全退出并重启 Claude Desktop

### 查看日志

日志文件位置：`logs/mcp-server.log`

**Linux/macOS:**
```bash
tail -f logs/mcp-server.log
```

**Windows:**
```powershell
Get-Content logs/mcp-server.log -Wait
```

## 高级配置

### 使用 HTTPS

如果您的 QVMConsole 使用 HTTPS：

```json
{
  "qvmconsole": {
    "base_url": "https://qvmconsole.example.com",
    "verify_ssl": true
  }
}
```

如果使用自签名证书，可以暂时禁用 SSL 验证（不推荐用于生产环境）：

```json
{
  "qvmconsole": {
    "verify_ssl": false
  }
}
```

### 调整日志级别

调试时可以设置更详细的日志：

```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

可用级别：`DEBUG`, `INFO`, `WARNING`, `ERROR`

## 安全建议

1. ✅ **使用专用 API Key** - 为 MCP Server 创建独立的用户账号和 API Key
2. ✅ **权限最小化** - 只授予必要的权限
3. ✅ **定期轮换** - 定期更换 API Key
4. ✅ **监控使用** - 在 QVMConsole 中查看 API Key 使用记录
5. ❌ **不要共享** - 不要将配置文件提交到 Git 或分享给他人

## 限制说明

当前版本（v0.1.0）的限制：

- ✅ 支持从模板创建虚拟机
- ✅ 支持查看虚拟机信息和密码
- ✅ 支持编辑虚拟机配置
- ❌ 不支持虚拟机电源操作（启动/关机/重启）
- ❌ 不支持快照管理
- ❌ 不支持删除虚拟机
- ❌ 不支持磁盘管理

这些功能将在后续版本中添加。

## 获取帮助

- 查看项目文档：[mcp-server-design.md](mcp-server-design.md)
- QVMConsole 文档：https://qvmcdocs.xiaozhuhouses.asia/
- 提交 Issue：（项目 GitHub 地址）
