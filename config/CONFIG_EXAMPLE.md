# 配置示例文档

## 方式一：通过 Claude Desktop 配置（推荐）

在 Claude Desktop 配置文件中直接配置环境变量：

```json
{
  "mcpServers": {
    "qvmconsole": {
      "command": "npx",
      "args": ["-y", "@qvmconsole/mcp-server"],
      "env": {
        "QVMC_BASE_URL": "http://192.168.1.100:8082",
        "QVMC_API_KEY_ID": "kvm_id_xxxxxxxxxxxxxxxxxx",
        "QVMC_API_KEY": "kvm_sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "QVMC_TIMEOUT": "30",
        "QVMC_VERIFY_SSL": "true"
      }
    }
  }
}
```

## 方式二：通过配置文件

创建 `config/config.json` 文件：

```json
{
  "qvmconsole": {
    "base_url": "http://192.168.1.100:8082",
    "api_key_id": "kvm_id_xxxxxxxxxxxxxxxxxx",
    "api_key": "kvm_sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "timeout": 30,
    "verify_ssl": true
  },
  "logging": {
    "level": "INFO",
    "file": "logs/mcp-server.log"
  }
}
```

## 方式三：通过系统环境变量

```bash
# Linux / macOS
export QVMC_BASE_URL="http://192.168.1.100:8082"
export QVMC_API_KEY_ID="kvm_id_xxxxxxxxxxxxxxxxxx"
export QVMC_API_KEY="kvm_sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export QVMC_TIMEOUT="30"
export QVMC_VERIFY_SSL="true"

# Windows PowerShell
$env:QVMC_BASE_URL="http://192.168.1.100:8082"
$env:QVMC_API_KEY_ID="kvm_id_xxxxxxxxxxxxxxxxxx"
$env:QVMC_API_KEY="kvm_sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
$env:QVMC_TIMEOUT="30"
$env:QVMC_VERIFY_SSL="true"
```

## 配置优先级

1. 环境变量（最高优先级）
2. 配置文件 `config/config.json`
3. 默认值

## 获取 API Key

1. 登录 QVMConsole 管理面板
2. 进入 **个人中心** → **API Key 管理**
3. 点击 **生成 API Key**
4. 复制生成的 `API Key ID` 和 `API Key`
