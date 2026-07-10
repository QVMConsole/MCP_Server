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

**重要：必须生成 Automation 类型的令牌，并且需要绕过 2FA 权限**

1. 登录 npmjs.com
2. 点击头像 → "Access Tokens"
3. 点击 "Generate New Token" → "Classic Token"
4. 选择 **"Automation"**（用于 CI/CD）
5. **重要：** 勾选 "Bypass 2FA for automation" 选项
6. 复制生成的 token（形如 `npm_xxxxxxxxxxxxxxxxxxxx`）

**注意：** 
- 如果你的账号启用了 2FA（双因素认证），必须使用具有 "Bypass 2FA" 权限的令牌
- Automation 类型的令牌可以绕过 2FA，适合 CI/CD 使用
- 不要使用 "Publish" 类型的令牌，它不能绕过 2FA

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

### 发布失败：EOTP - Requires one-time password

**错误信息：**
```
npm error code EOTP
npm error This operation requires a one-time password from your authenticator.
```

**原因：** 你的 npm 账号启用了双因素认证（2FA），但使用的令牌没有绕过 2FA 的权限。

**解决方案：**

#### 步骤 1: 删除所有旧令牌

访问 https://www.npmjs.com/settings/YOUR_USERNAME/tokens，删除所有现有令牌。

#### 步骤 2: 生成新的 Automation 令牌

**关键：必须选择 Classic Token 的 Automation 类型**

1. 点击 "Generate New Token"
2. 选择 **"Classic Token"**（不要选 Granular）
3. 选择 **"Automation"**（不要选 Publish）
4. Automation 类型令牌**默认可以绕过 2FA**
5. 复制令牌

#### 步骤 3: 更新 GitHub Secrets

1. 进入 GitHub 仓库 Settings → Secrets and variables → Actions
2. **删除**旧的 `NPM_TOKEN`
3. **新建** `NPM_TOKEN` 并粘贴新令牌

#### 步骤 4: 如果是组织包

如果你的包是 `@qvmconsole/mcp-server`：

1. 检查你是否是 `qvmconsole` 组织的成员
2. 检查组织的 2FA 设置：https://www.npmjs.com/settings/qvmconsole/security
3. 如果组织强制要求 2FA，可以临时关闭（发布后重新启用）

**详细指南：** 参考 [NPM_2FA_FIX.md](NPM_2FA_FIX.md)

**错误信息：**
```
403 Forbidden - Two-factor authentication or granular access token 
with bypass 2fa enabled is required to publish packages.
```

**解决方案：**

#### 方案一：使用 Automation 令牌（推荐）

1. 删除现有的 `NPM_TOKEN`
2. 重新生成 npm token：
   - 登录 npmjs.com → Access Tokens → Generate New Token
   - 选择 **"Classic Token"** → **"Automation"**
   - **必须勾选** "Bypass 2FA for automation"
   - 复制新令牌并更新 GitHub Secrets 中的 `NPM_TOKEN`

#### 方案二：使用 Granular Access Token（新方式）

1. 登录 npmjs.com
2. Access Tokens → Generate New Token → **"Granular Access Token"**
3. 配置权限：
   - **Packages**: 选择你的包或所有包
   - **Permissions**: 勾选 "Read and write"
   - **2FA**: 勾选 "Bypass two-factor authentication"
4. 复制令牌并更新 GitHub Secrets

#### 方案三：关闭组织的 2FA 要求（不推荐）

如果是组织包（@qvmconsole/），可以在组织设置中临时关闭 2FA 要求：
- 组织设置 → Security → 取消勾选 "Require two-factor authentication"
- 发布后重新启用

**重要提示：**
- CI/CD 发布必须使用具有 "Bypass 2FA" 权限的令牌
- 普通的 "Publish" 令牌无法在自动化环境中使用
- 确保令牌类型为 "Automation" 或 "Granular Access Token"

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
