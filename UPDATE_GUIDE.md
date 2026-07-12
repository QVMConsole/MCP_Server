# 更新本地 MCP Server

## 方式一：使用 npx（推荐，自动更新）

如果你在 Claude Desktop 配置中使用的是 npx：

```json
{
  "mcpServers": {
    "qvmconsole": {
      "command": "npx",
      "args": ["-y", "@qvmconsole/mcp-server"]
    }
  }
}
```

**npx 会自动使用最新版本**，但如果需要强制清除缓存：

### Windows
```powershell
# 清除 npx 缓存
Remove-Item -Recurse -Force $env:LOCALAPPDATA\npm-cache\_npx\*qvmconsole*

# 或者清除所有 npx 缓存
npx clear-npx-cache
```

### macOS/Linux
```bash
# 清除 npx 缓存
rm -rf ~/.npm/_npx/@qvmconsole

# 或者
npx clear-npx-cache
```

然后重启 Claude Desktop。

---

## 方式二：全局安装方式

如果你使用全局安装：

```bash
npm install -g @qvmconsole/mcp-server
```

更新命令：

```bash
# 更新到最新版本
npm update -g @qvmconsole/mcp-server


# 或者重新安装
npm install -g @qvmconsole/mcp-server@latest
```

---

## 方式三：从源码运行

如果你从源码运行，直接拉取最新代码：

```bash
cd "C:\Users\17737\Code\Opensource\QVMConsole\Code\MCP Server"
git pull origin main
pip install -r requirements.txt
```

---

## 查看当前版本

### 使用 npx
```bash
npx @qvmconsole/mcp-server --version
```

### 使用全局安装
```bash
qvmconsole-mcp --version
```

### 查看 npm 上的最新版本
```bash
npm view @qvmconsole/mcp-server version
```

---

## 推荐做法

使用 npx 方式最简单，因为：
- ✅ 无需手动更新
- ✅ 每次运行自动使用最新版本
- ✅ 不占用全局 npm 空间
- ✅ 适合多项目使用不同版本

只需要在 Claude Desktop 配置中使用 `npx` 即可。
