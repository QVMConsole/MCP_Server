# QVMConsole MCP Server - 快速开始指南

## 第一步：获取 API Key

1. 登录 QVMConsole 管理面板 (http://your-server:8082)
2. 点击右上角用户名 → **个人中心**
3. 左侧菜单选择 **API Key 管理**
4. 点击 **生成 API Key** 按钮
5. 完成二次验证
6. **立即复制** API Key ID 和 API Key（只显示一次！）

## 第二步：配置 MCP Server

编辑 `config/config.json`，填入你的配置：

```json
{
  "qvmconsole": {
    "base_url": "http://your-qvmconsole-server:8082",
    "api_key_id": "kvm_id_你的KeyID",
    "api_key": "kvm_sk_你的完整APIKey",
    "timeout": 30,
    "verify_ssl": true
  }
}
```

## 第三步：配置 Claude Desktop

### Windows

1. 打开配置文件：
   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```

2. 添加配置：
   ```json
   {
     "mcpServers": {
       "qvmconsole": {
         "command": "python",
         "args": [
           "C:\\Users\\你的用户名\\路径\\QVMConsole-MCP-Server\\src\\server.py"
         ]
       }
     }
   }
   ```

### macOS

1. 打开配置文件：
   ```bash
   nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. 添加配置：
   ```json
   {
     "mcpServers": {
       "qvmconsole": {
         "command": "python3",
         "args": [
           "/Users/你的用户名/路径/QVMConsole-MCP-Server/src/server.py"
         ]
       }
     }
   }
   ```

## 第四步：重启 Claude Desktop

完全退出并重新启动 Claude Desktop。

## 第五步：测试

在 Claude 中输入：

```
列出所有可用的虚拟机模板
```

如果看到模板列表，说明配置成功！

## 常用命令示例

### 查看模板
```
列出所有虚拟机模板
```

### 创建虚拟机
```
使用 ubuntu-22.04 模板创建虚拟机 test-vm，2核4G内存，50GB磁盘
```

### 查看虚拟机信息（含密码）
```
查看 test-vm 的详细信息，包括登录密码
```

### 列出所有虚拟机
```
列出所有虚拟机
```

### 修改配置
```
将 test-vm 的内存调整为 8GB
```

## 故障排查

### 问题：找不到配置文件

**解决方法：**
```bash
cp config/config.example.json config/config.json
```
然后编辑 config/config.json

### 问题：API 凭证无效

**解决方法：**
1. 检查 API Key ID 和 API Key 是否正确
2. 确认没有多余的空格或换行
3. 在 QVMConsole 管理面板检查 API Key 是否被撤销

### 问题：连接超时

**解决方法：**
1. 检查 base_url 是否正确（注意端口号）
2. 确认 QVMConsole 服务正在运行
3. 检查防火墙设置

### 查看日志

日志文件位置：`logs/mcp-server.log`

Windows:
```cmd
type logs\mcp-server.log
```

macOS/Linux:
```bash
tail -f logs/mcp-server.log
```

## 支持

- 详细文档：[docs/usage.md](docs/usage.md)
- 设计文档：[docs/mcp-server-design.md](docs/mcp-server-design.md)
- QVMConsole 文档：https://qvmcdocs.xiaozhuhouses.asia/
