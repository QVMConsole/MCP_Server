# QVMConsole MCP Server

[QVMConsole](https://github.com/qvmconsole/qvmconsole) 的 MCP (Model Context Protocol) Server，使 AI 助手能够通过自然语言管理虚拟机。

## 功能特性

- 🔍 **查看模板列表** - 浏览所有可用的虚拟机模板
- 🚀 **创建虚拟机** - 从模板快速创建虚拟机（支持自定义配置）
- 📊 **查看虚拟机信息** - 获取详细信息，包括登录密码
- 📝 **列出虚拟机** - 查看所有虚拟机及其状态
- ⚙️ **编辑虚拟机** - 修改 CPU、内存等配置

## 系统要求

- Python 3.10+
- 一个运行中的 QVMConsole 实例
- 有效的 API Key（从 QVMConsole 管理面板获取）

## 安装

### 1. 克隆项目

```bash
git clone <repo-url>
cd QVMConsole-MCP-Server
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置

复制配置文件模板并填写您的配置：

```bash
cp config/config.example.json config/config.json
```

编辑 `config/config.json`，填入您的 QVMConsole 地址和 API Key：

```json
{
  "qvmconsole": {
    "base_url": "http://your-qvmconsole-url:8082",
    "api_key_id": "kvm_id_xxxxxxxxxxxxxxxxxx",
    "api_key": "kvm_sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "timeout": 30,
    "verify_ssl": true
  }
}
```

#### 获取 API Key

1. 登录 QVMConsole 管理面板
2. 进入 **个人中心** → **API Key 管理**
3. 点击 **生成 API Key**
4. 复制生成的 `API Key ID` 和 `API Key` 到配置文件

## 使用方法

### 在 Claude Desktop 中使用

在 Claude Desktop 的配置文件中添加：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "qvmconsole": {
      "command": "python",
      "args": [
        "/path/to/QVMConsole-MCP-Server/src/server.py"
      ]
    }
  }
}
```

重启 Claude Desktop 后即可使用。

### 直接运行测试

```bash
python src/server.py
```

## 使用示例

在 Claude Desktop 中，您可以使用自然语言与虚拟机交互：

- "列出所有可用的虚拟机模板"
- "使用 ubuntu-22.04 模板创建一个虚拟机，名称为 test-vm，2核4G"
- "查看 test-vm 的详细信息，包括登录密码"
- "将 test-vm 的内存调整为 8G"
- "列出所有虚拟机"

## 可用工具

### 1. list_templates
列出所有可用的虚拟机模板。

### 2. create_vm_from_template
从模板创建虚拟机。

**参数：**
- `template_name` (必填) - 模板名称
- `vm_name` (必填) - 虚拟机名称
- `vcpu` (必填) - CPU 核心数
- `ram` (必填) - 内存大小（GB）
- `disk_size` (可选) - 磁盘大小（GB）
- `hostname` (可选) - 主机名
- `password` (可选) - 登录密码（不填则自动生成）
- `user` (可选) - 用户名
- `autostart` (可选) - 是否自动启动
- `remark` (可选) - 备注信息

### 3. get_vm_info
获取虚拟机详细信息，包括登录密码。

**参数：**
- `vm_name` (必填) - 虚拟机名称
- `show_password` (可选) - 是否显示密码，默认 true

### 4. list_vms
列出所有虚拟机及其基本状态。

### 5. edit_vm
编辑虚拟机配置。

**参数：**
- `vm_name` (必填) - 虚拟机名称
- `vcpu` (可选) - CPU 核心数
- `ram` (可选) - 内存大小（GB）
- `remark` (可选) - 备注信息
- `autostart` (可选) - 是否自动启动

## 日志

日志文件默认保存在 `logs/mcp-server.log`，可在配置文件中修改。

## 故障排查

### API Key 无效

确保您的 API Key 正确且未被撤销，在 QVMConsole 管理面板中检查 API Key 状态。

### 连接失败

检查：
1. QVMConsole 服务是否运行
2. `base_url` 配置是否正确
3. 网络连接是否正常
4. 防火墙设置是否允许连接

### 权限不足

确保 API Key 对应的用户有足够的权限执行相应操作。

## 安全提示

- 🔐 不要将 `config/config.json` 提交到版本控制系统
- 🔑 妥善保管您的 API Key
- 🛡️ 建议在生产环境使用 HTTPS
- 👤 为 MCP Server 创建专用的受限权限用户

## 开发

### 运行测试

```bash
pytest tests/
```

### 项目结构

```
QVMConsole-MCP-Server/
├── src/
│   ├── __init__.py
│   ├── server.py      # MCP Server 主入口
│   ├── client.py      # QVMConsole API 客户端
│   ├── tools.py       # MCP 工具实现
│   └── config.py      # 配置管理
├── config/
│   └── config.example.json
├── docs/
│   ├── mcp-server-design.md
│   └── usage.md
├── tests/
├── requirements.txt
└── README.md
```

## 许可证

Apache License 2.0

## 相关链接

- [QVMConsole 官网](https://www.qvmconsole.cn/)
- [QVMConsole 文档](https://qvmcdocs.xiaozhuhouses.asia/)
- [MCP Protocol](https://modelcontextprotocol.io/)
