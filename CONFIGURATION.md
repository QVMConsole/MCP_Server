# 配置变更说明

## v0.2.0 - 支持环境变量配置

### 新特性

现在可以直接在 Claude Desktop 配置中使用 `env` 字段配置 API 密钥，无需创建单独的配置文件！

### 使用示例

```json
{
  "mcpServers": {
    "qvmconsole": {
      "command": "npx",
      "args": ["-y", "@qvmconsole/mcp-server"],
      "env": {
        "QVMC_BASE_URL": "http://192.168.1.100:8082",
        "QVMC_API_KEY_ID": "kvm_id_xxxxxxxxxxxxxxxxxx",
        "QVMC_API_KEY": "kvm_sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

### 配置方式

支持三种配置方式（按优先级排序）：

1. **环境变量** - 通过 Claude Desktop 的 `env` 字段或系统环境变量
2. **配置文件** - `config/config.json`
3. **默认值**

### 环境变量

- `QVMC_BASE_URL` - QVMConsole 地址（必需）
- `QVMC_API_KEY_ID` - API Key ID（必需）
- `QVMC_API_KEY` - API Key（必需）
- `QVMC_TIMEOUT` - 请求超时时间（可选，默认 30）
- `QVMC_VERIFY_SSL` - 是否验证 SSL（可选，默认 true）

### 向后兼容

旧的配置文件方式仍然支持。如果同时存在环境变量和配置文件，环境变量优先。

### 迁移指南

#### 从配置文件迁移

**旧方式** (config/config.json):
```json
{
  "qvmconsole": {
    "base_url": "http://192.168.1.100:8082",
    "api_key_id": "kvm_id_xxx",
    "api_key": "kvm_sk_xxx"
  }
}
```

**新方式** (Claude Desktop 配置):
```json
{
  "mcpServers": {
    "qvmconsole": {
      "command": "npx",
      "args": ["-y", "@qvmconsole/mcp-server"],
      "env": {
        "QVMC_BASE_URL": "http://192.168.1.100:8082",
        "QVMC_API_KEY_ID": "kvm_id_xxx",
        "QVMC_API_KEY": "kvm_sk_xxx"
      }
    }
  }
}
```

现在配置都在一个地方，更简洁！
