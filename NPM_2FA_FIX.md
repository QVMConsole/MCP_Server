# npm 2FA 问题快速解决指南

## 错误症状

GitHub Actions 发布时报错：
```
npm error code EOTP
npm error This operation requires a one-time password from your authenticator.
```

## 根本原因

**你的 npm 账号启用了双因素认证（2FA），但使用的令牌没有绕过 2FA 的权限。**

## 快速解决步骤

### 步骤 1: 检查你的账号类型

访问：https://www.npmjs.com/settings/YOUR_USERNAME/profile

查看是否启用了 2FA（Two-Factor Authentication）。

### 步骤 2: 删除所有旧令牌

1. 访问：https://www.npmjs.com/settings/YOUR_USERNAME/tokens
2. 删除所有现有的令牌（避免混淆）

### 步骤 3: 生成正确的令牌

**关键：必须选择 Classic Token 的 Automation 类型**

1. 点击 "Generate New Token"
2. 选择 **"Classic Token"**（不要选 Granular Access Token）
3. 选择 **"Automation"**（不要选 Publish）
4. 复制令牌（形如 `npm_xxxxxxxxxxxxxxxxxxxx`）

**为什么选择 Automation？**
- Automation 类型的令牌**默认可以绕过 2FA**
- 专门为 CI/CD 设计
- 不需要手动输入 OTP

### 步骤 4: 更新 GitHub Secrets

1. 进入你的 GitHub 仓库
2. Settings → Secrets and variables → Actions
3. **删除** 旧的 `NPM_TOKEN`（如果有）
4. **新建** `NPM_TOKEN`
5. 粘贴刚才复制的令牌
6. 点击 "Add secret"

### 步骤 5: 重新触发发布

1. 进入 GitHub 仓库的 Actions 页面
2. 选择 "Publish to npm" 工作流
3. 点击 "Run workflow"
4. 填写版本信息并运行

## 如果还是失败怎么办？

### 方案 A: 检查是否是组织包

如果你的包是 `@qvmconsole/mcp-server` 这样的组织包：

1. **检查你是否是组织成员**
   - 访问：https://www.npmjs.com/settings/qvmconsole/members
   - 确保你的账号在列表中

2. **检查组织的 2FA 设置**
   - 访问：https://www.npmjs.com/settings/qvmconsole/security
   - 如果启用了 "Require two-factor authentication for write access"
   - 可以临时关闭这个选项（发布后再开启）

3. **或者：创建组织级别的 Automation Token**
   - 在组织设置中生成令牌
   - 而不是在个人账号中生成

### 方案 B: 临时关闭 2FA（不推荐）

**仅在测试时使用：**

1. 访问：https://www.npmjs.com/settings/YOUR_USERNAME/profile
2. 在 Two-Factor Authentication 部分点击 "Modify 2FA"
3. 临时关闭 2FA
4. 发布包
5. **立即重新启用 2FA**

**风险：** 关闭 2FA 期间账号安全性降低

### 方案 C: 使用 Granular Access Token

如果 Classic Automation Token 不工作，尝试 Granular Access Token：

1. Generate New Token → **"Granular Access Token"**
2. 配置：
   - **Expiration**: 设置过期时间（如 90 天）
   - **Packages and scopes**: 选择 "Only select packages and scopes"
   - 勾选你的包：`@qvmconsole/mcp-server`
   - **Permissions**: 勾选 "Read and write"
   - **⚠️ 关键**: 在 "Organizations and repositories" 下面，找到 "Two-factor authentication"
   - ✅ **必须勾选** "Bypass two-factor authentication"
3. 生成并复制令牌
4. 更新 GitHub Secrets

## 验证令牌是否正确

在本地测试：

```bash
# 设置令牌
export NPM_TOKEN="你的令牌"

# 或 Windows PowerShell
$env:NPM_TOKEN="你的令牌"

# 创建 .npmrc
echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" > .npmrc

# 测试发布（干运行）
npm publish --dry-run
```

**如果要求输入 OTP，说明令牌配置不正确，需要重新生成。**

## 总结

✅ **正确做法：**
1. 使用 **Classic Token** 的 **Automation** 类型
2. Automation 令牌默认可以绕过 2FA
3. 删除旧令牌，生成新令牌
4. 更新 GitHub Secrets
5. 重新运行工作流

❌ **常见错误：**
1. 使用 "Publish" 类型的令牌（不能绕过 2FA）
2. 使用 Granular Token 但没有勾选 "Bypass 2FA"
3. 令牌权限不足
4. 组织设置强制要求 2FA
