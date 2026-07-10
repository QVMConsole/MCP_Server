# npm 令牌配置说明

## 问题描述

发布时遇到错误：

**错误 1：403 Forbidden**
```
403 Forbidden - Two-factor authentication or granular access token 
with bypass 2fa enabled is required to publish packages.
```

**错误 2：EOTP（需要一次性密码）**
```
EOTP - This operation requires a one-time password from your authenticator.
```

这些错误都是因为 npm 的双因素认证（2FA）限制了自动化发布。

## 解决方案

### ⚠️ 重要：生成令牌时必须明确选择绕过 2FA

npm 现在有两种生成令牌的方式，必须选择正确的选项：

### 方案一：使用 Classic Automation Token（推荐，简单）

这是最简单可靠的方案：

1. **登录 npmjs.com**
2. **删除所有旧令牌**
   - 进入 Access Tokens 页面
   - 删除之前生成的所有令牌（避免混淆）

3. **生成新的 Automation 令牌**
   - 点击 "Generate New Token"
   - 选择 **"Classic Token"**（不是 Granular）
   - 选择 **"Automation"**
   
4. **确认令牌权限**
   - Automation 类型的令牌**默认就可以绕过 2FA**
   - 不需要额外勾选任何选项
   - 如果界面上有 "Bypass 2FA" 选项，确保它是启用状态

5. **复制令牌**
   - 复制生成的令牌（形如 `npm_xxxxxxxxxxxxxxxxxxxx`）
   - **注意：令牌只显示一次，请妥善保存**

6. **更新 GitHub Secrets**
   - 进入 GitHub 仓库
   - Settings → Secrets and variables → Actions
   - **删除** 旧的 `NPM_TOKEN`
   - **新建** `NPM_TOKEN` 并粘贴新令牌

### 方案二：使用 Granular Access Token（新方式）

这是 npm 推荐的新方式，可以更细粒度地控制权限：

1. **登录 npmjs.com**
2. **进入 Access Tokens**
   - 点击右上角头像 → "Access Tokens"

3. **生成 Granular Access Token**
   - 点击 "Generate New Token"
   - 选择 **"Granular Access Token"**

4. **配置令牌权限**
   - **Token name**: 填写令牌名称（如 `GitHub Actions CI`）
   - **Expiration**: 选择过期时间（建议 1 年）
   - **Packages and scopes**:
     - 选择 "Only select packages and scopes"
     - 勾选你要发布的包（如 `@qvmconsole/mcp-server`）
   - **Permissions**:
     - 勾选 **"Read and write"**
   - **2FA (Two-Factor Authentication)**:
     - **必须勾选** ✅ **"Bypass two-factor authentication"**

5. **生成并复制令牌**
   - 点击 "Generate token"
   - 复制生成的令牌

6. **更新 GitHub Secrets**
   - 同方案一

### 方案三：在组织中配置（如果使用 @qvmconsole/）

如果你的包是组织包（带 @ 前缀），需要确保：

1. **你是组织成员**
   - 访问：https://www.npmjs.com/settings/qvmconsole/members
   - 确保你的账号在成员列表中

2. **你有发布权限**
   - 在组织成员列表中，确保你的角色是 "owner" 或 "admin"

3. **组织允许 Automation tokens**
   - 访问：https://www.npmjs.com/settings/qvmconsole/security
   - 确保没有限制 Automation tokens

## 验证令牌

可以在本地测试令牌是否有效：

```bash
# 设置令牌
export NPM_TOKEN="npm_xxxxxxxxxxxxxxxxxxxx"

# 或 Windows PowerShell
$env:NPM_TOKEN="npm_xxxxxxxxxxxxxxxxxxxx"

# 登录测试
echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" > .npmrc
npm whoami

# 测试发布（干运行）
npm publish --dry-run
```

## 常见问题

### Q1: 我已经有 Automation token，为什么还是要求 OTP？

**A: 可能的原因：**

1. **令牌生成时没有正确配置**
   - 解决：删除旧令牌，严格按照上述步骤重新生成
   - 确保选择的是 "Classic Token" 的 "Automation" 类型

2. **账号启用了组织级别的 2FA 强制要求**
   - 如果包属于组织（如 @qvmconsole/），需要检查组织设置
   - 解决：去组织设置中关闭强制 2FA，或者使用个人账号发布

3. **使用了 Granular Access Token 但没有勾选 Bypass 2FA**
   - 解决：重新生成并确保勾选 "Bypass two-factor authentication"

4. **令牌权限不足**
   - 解决：确保令牌有 "publish" 权限

**验证令牌类型：**
```bash
# 使用令牌登录后检查
npm profile get
```

如果显示需要 OTP，说明令牌没有绕过 2FA 的权限。

### Q2: 我不想关闭 2FA，有其他办法吗？

A: 不需要关闭 2FA！使用 **Automation** 或 **Granular Access Token（勾选 Bypass 2FA）** 即可。

### Q3: Granular Access Token 和 Classic Token 有什么区别？

A: 
- **Classic Token**: 简单易用，但权限较宽泛
- **Granular Access Token**: 更安全，可以精确控制权限范围，推荐使用

### Q4: 令牌会过期吗？

A: 
- Classic Automation Token: 默认不过期
- Granular Access Token: 可以设置过期时间，建议设置 1 年并定期更新

## 安全建议

1. ✅ 使用 Granular Access Token，只授予必要的权限
2. ✅ 设置令牌过期时间，定期更新
3. ✅ 使用不同的令牌用于不同的项目或 CI/CD
4. ✅ 定期审查和删除不再使用的令牌
5. ❌ 不要在代码或公开仓库中泄露令牌
6. ❌ 不要使用个人账号密码在 CI/CD 中登录

## 参考链接

- [npm Tokens 文档](https://docs.npmjs.com/about-access-tokens)
- [npm Granular Access Tokens](https://docs.npmjs.com/creating-and-viewing-access-tokens)
- [npm 自动化最佳实践](https://docs.npmjs.com/using-private-packages-in-a-ci-cd-workflow)
