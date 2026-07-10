# 发布到 npm 的步骤

## 前置准备

### 1. 创建 npm 账号
如果还没有 npm 账号，请访问 https://www.npmjs.com/signup 注册。

### 2. 创建组织（可选但推荐）
1. 登录 npmjs.com
2. 点击头像 → "Add Organization"
3. 创建名为 `qvmconsole` 的组织
4. 这样可以使用 `@qvmconsole/mcp-server` 这个包名

### 3. 生成 npm 访问令牌
1. 登录 npmjs.com
2. 点击头像 → "Access Tokens"
3. 点击 "Generate New Token" → "Classic Token"
4. 选择 "Automation"（用于 CI/CD）
5. 复制生成的 token（形如 `npm_xxxxxxxxxxxxxxxxxxxx`）

### 4. 配置 GitHub Secrets
1. 进入 GitHub 仓库
2. 点击 "Settings" → "Secrets and variables" → "Actions"
3. 点击 "New repository secret"
4. 名称填写: `NPM_TOKEN`
5. 值粘贴刚才复制的 npm token
6. 点击 "Add secret"

## 发布方式

### 方式一：通过 Git 标签自动发布（推荐）

```bash
# 1. 确保所有改动已提交
git add .
git commit -m "准备发布 v0.1.0"

# 2. 创建并推送标签
git tag v0.1.0
git push origin v0.1.0

# 3. GitHub Actions 会自动触发发布流程
```

### 方式二：手动触发发布

1. 进入 GitHub 仓库
2. 点击 "Actions" 标签
3. 选择 "Publish to npm" 工作流
4. 点击 "Run workflow"
5. 选择分支后点击 "Run workflow"

### 方式三：本地手动发布

```bash
# 1. 登录 npm
npm login

# 2. 检查包内容
npm pack --dry-run

# 3. 发布
npm publish --access public
```

## 版本管理

### 更新版本号

```bash
# 补丁版本 (0.1.0 -> 0.1.1)
npm version patch

# 次要版本 (0.1.0 -> 0.2.0)
npm version minor

# 主要版本 (0.1.0 -> 1.0.0)
npm version major
```

### 发布新版本

```bash
# 1. 更新版本
npm version patch  # 或 minor / major

# 2. 推送提交和标签
git push && git push --tags

# 3. GitHub Actions 自动发布
```

## 验证发布

### 检查包是否发布成功

```bash
# 查看包信息
npm view @qvmconsole/mcp-server

# 测试安装
npx @qvmconsole/mcp-server
```

### 在 npmjs.com 上查看
访问: https://www.npmjs.com/package/@qvmconsole/mcp-server

## 故障排查

### 发布失败：401 Unauthorized
- 检查 `NPM_TOKEN` 是否正确设置在 GitHub Secrets 中
- 确认 token 有发布权限（Automation 类型）
- 确认 token 没有过期

### 发布失败：403 Forbidden
- 如果使用 `@qvmconsole/` 前缀，确保已创建 `qvmconsole` 组织
- 确保你的 npm 账号是该组织的成员
- 或者修改 package.json 中的 name 为不带 @ 的名称

### 发布失败：包名已存在
- 包名可能被占用
- 修改 package.json 中的 name 字段

### Python 依赖安装失败
- 用户需要确保系统安装了 Python 3.10+
- 用户可以手动运行 `pip install -r requirements.txt`

## 最佳实践

1. **语义化版本**: 遵循 [Semantic Versioning](https://semver.org/)
2. **变更日志**: 在 CHANGELOG.md 中记录每个版本的变更
3. **测试**: 发布前在本地测试 `npm pack` 和 `npx` 安装
4. **文档**: 保持 README.md 与最新版本同步
