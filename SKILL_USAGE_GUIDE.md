# QVMConsole MCP Skill 使用指南

## 📌 快速开始

### 给 AI 模型的指令

当你需要使用 QVMConsole MCP 管理虚拟机时，请参考这个 Skill 文件：

```
请使用 qvmconsole-vm-management skill 来帮我创建虚拟机
```

## 🎯 完整开发测试流程

### 标准流程（必须按此顺序执行）

#### 1️⃣ 获取所有可用模板
```
请列出所有可用的虚拟机模板
```

**AI 会调用**: `list_templates`

**预期输出**: 模板列表，包括名称、类型、状态

---

#### 2️⃣ 创建虚拟机（重要：必须包含必需参数）

```
使用 Ubuntu26.04-LTS 模板创建一个虚拟机，配置 2 核 CPU 和 4GB 内存
```

**AI 必须提供的参数**:
- ✅ `template_name`: 模板名称
- ✅ `vm_name`: 虚拟机名称
- ✅ `vcpu`: CPU 核心数
- ✅ `ram`: 内存大小
- ✅ `user`: 用户名（Linux 模板必需）
- ✅ `password`: 密码（Linux 模板必需）

**示例调用**:
```python
create_vm_from_template(
    template_name="Ubuntu26.04-LTS",
    vm_name="test-ubuntu-vm",
    vcpu=2,
    ram=4,
    user="ubuntu",
    password="SecurePass123"
)
```

**预期输出**: 任务 ID

---

#### 3️⃣ 等待虚拟机创建完成

**关键**: 必须等待 **20 秒**，让虚拟机完成初始化

```
等待 20 秒...
```

---

#### 4️⃣ 获取虚拟机信息（包含账号密码）

```
查看虚拟机的详细信息和登录凭据
```

**AI 会调用**: `get_vm_info`

**预期输出**:
- IP 地址
- 用户名
- 密码
- 状态
- 配置信息

---

#### 5️⃣ 使用 SSH 连接测试

AI 应该提供 SSH 连接命令：

```
SSH 连接命令：
ssh ubuntu@192.168.1.100

密码：SecurePass123
```

如果有 SSH MCP 工具，可以直接测试连接：

```
让我测试 SSH 连接...

[使用 SSH MCP 连接]
[执行命令: uname -a]
[执行命令: free -h]
[执行命令: df -h]

✅ SSH 连接测试成功！
```

---

## ⚠️ 关键注意事项

### 1. Linux 模板必需参数

**错误示例** ❌:
```python
# 缺少 user 和 password
create_vm_from_template(
    template_name="Ubuntu26.04-LTS",
    vm_name="test-vm",
    vcpu=2,
    ram=4
)
# 结果：API 返回 "请输入用户名"
```

**正确示例** ✅:
```python
# 包含所有必需参数
create_vm_from_template(
    template_name="Ubuntu26.04-LTS",
    vm_name="test-vm",
    vcpu=2,
    ram=4,
    user="ubuntu",        # 必需
    password="Pass123"    # 必需
)
```

### 2. 常见用户名

| 模板类型 | 默认用户名 |
|---------|-----------|
| Ubuntu | ubuntu |
| Debian | debian |
| CentOS/RHEL | root 或 centos |
| Generic Linux | root |

### 3. 密码要求

- 长度：至少 8 位
- 复杂度：建议包含大小写字母、数字
- 安全性：不要使用 "123456"、"password" 等常见密码

### 4. 等待时间

- **创建后必须等待**: 20 秒
- **原因**: 虚拟机需要时间启动并获取 IP 地址
- **不等待的后果**: 获取不到 IP 地址和完整信息

---

## 📋 完整示例对话

### 示例：创建并测试 Ubuntu 虚拟机

**用户**: 帮我创建一个 Ubuntu 虚拟机用于测试

**AI 响应流程**:

```markdown
好的，我来帮你创建一个 Ubuntu 虚拟机。

【步骤 1】首先查看可用模板
[调用 list_templates]

找到可用模板：Ubuntu26.04-LTS ✅

【步骤 2】创建虚拟机
配置信息：
- 模板：Ubuntu26.04-LTS
- 名称：ubuntu-test-vm
- CPU：2 核
- 内存：4 GB
- 用户名：ubuntu
- 密码：Test@2024Secure

[调用 create_vm_from_template 并传入所有必需参数]

✅ 虚拟机创建任务已提交
任务 ID: 123

【步骤 3】等待虚拟机初始化
正在等待虚拟机启动...（约需 20 秒）
[等待 20 秒]

【步骤 4】获取虚拟机信息
[调用 get_vm_info]

✅ 虚拟机已创建并启动成功！

📋 虚拟机信息：
- 名称：ubuntu-test-vm
- IP 地址：192.168.1.100
- 状态：running
- CPU：2 核
- 内存：4 GB

🔐 登录凭据：
- 用户名：ubuntu
- 密码：Test@2024Secure

【步骤 5】SSH 连接命令
ssh ubuntu@192.168.1.100

密码：Test@2024Secure

【步骤 6】测试连接（如果有 SSH MCP）
[使用 SSH MCP 连接虚拟机]
[执行: uname -a]
[执行: free -h]

✅ SSH 连接测试成功！虚拟机运行正常。
```

---

## 🔧 故障排除

### 问题 1: "请输入用户名"

**原因**: 缺少 `user` 参数

**解决**: 添加 `user` 和 `password` 参数

```python
# 添加这两个参数
user="ubuntu"
password="YourPassword123"
```

---

### 问题 2: "磁盘空间不足"

**解决流程**:

1. 检查存储池
```
[调用 list_storage_pools]
```

2. 选择有空间的存储池
```python
create_vm_from_template(
    # ... 其他参数
    storage_pool_id="pool-with-space"  # 添加此参数
)
```

---

### 问题 3: 无法获取 IP 地址

**原因**: 没有等待足够时间

**解决**: 创建后等待 20 秒再查询虚拟机信息

---

## 📚 相关文档

- 完整 Skill 定义: [qvmconsole-vm-management.skill.md](qvmconsole-vm-management.skill.md)
- 使用文档: [docs/usage.md](docs/usage.md)
- 存储池功能: [STORAGE_POOL_FEATURE.md](STORAGE_POOL_FEATURE.md)

---

## ✅ 检查清单

在创建虚拟机前，确保：

- [ ] 已调用 `list_templates` 查看可用模板
- [ ] 选择了合适的模板
- [ ] 提供了 `user` 参数（Linux 模板）
- [ ] 提供了 `password` 参数（Linux 模板）
- [ ] 虚拟机名称是唯一的
- [ ] 创建后等待 20 秒
- [ ] 调用 `get_vm_info` 获取完整信息
- [ ] 提供了 SSH 连接命令
- [ ] （可选）测试了 SSH 连接

---

**创建日期**: 2026-07-10  
**适用版本**: QVMConsole MCP Server 0.1.0+
