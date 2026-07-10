---
name: "qvmconsole-vm-management"
description: "Manages QVMConsole virtual machines via MCP protocol. Invoke when user needs to create, query, or manage VMs, or mentions QVMConsole, KVM, virtual machines."
---

# QVMConsole 虚拟机管理

此技能通过 MCP 协议管理 QVMConsole 虚拟机平台，提供完整的虚拟机生命周期管理能力。

## 何时使用

**立即调用此技能当**：
- 用户需要创建、管理或查询虚拟机
- 用户需要查看可用的虚拟机模板
- 用户需要获取虚拟机的登录凭据
- 用户需要查看存储池信息
- 用户提到 QVMConsole、KVM、虚拟机、VM 等关键词

**不要使用**：
- 用户只是询问概念性问题而不需要实际操作
- 用户需要的是其他云平台（AWS、Azure、阿里云等）的虚拟机管理

## 可用 MCP 工具

### 1. list_templates
列出所有可用的虚拟机模板。

**使用场景**：在创建虚拟机之前查看可用模板

**示例**：
```
请列出所有可用的虚拟机模板
```

### 2. list_storage_pools
列出所有存储池及其可用空间信息。

**使用场景**：检查存储空间是否充足，选择合适的存储位置

**示例**：
```
请查看存储池的可用空间
```

### 3. create_vm_from_template
从模板创建虚拟机。

**必需参数**：
- `template_name`: 模板名称（从 list_templates 获取）
- `vm_name`: 虚拟机名称（必须唯一）
- `vcpu`: CPU 核心数
- `ram`: 内存大小（GB）
- `user`: 用户名（**Linux 模板必需**）
- `password`: 密码（**Linux 模板必需**）

**可选参数**：
- `disk_size`: 磁盘大小（GB）
- `hostname`: 主机名
- `storage_pool_id`: 存储池 ID
- `autostart`: 是否自动启动
- `remark`: 备注信息

**示例**：
```
使用 Ubuntu26.04-LTS 模板创建一个名为 test-vm 的虚拟机，配置 2 核 CPU 和 4GB 内存
```

### 4. get_vm_info
获取虚拟机详细信息，包括登录密码。

**必需参数**：
- `vm_name`: 虚拟机名称

**示例**：
```
查看 test-vm 虚拟机的详细信息和密码
```

### 5. list_vms
列出所有虚拟机及其状态。

### 6. edit_vm
编辑虚拟机配置。

## 标准工作流程

### 创建并测试虚拟机（完整流程）

当用户要求创建虚拟机时，**必须**按照以下步骤执行：

#### 步骤 1: 查询可用模板
```
首先，让我查看可用的虚拟机模板。
[调用 list_templates]
```

#### 步骤 2: 创建虚拟机
根据用户需求选择合适的模板。

**⚠️ 关键：Linux 模板必须提供 user 和 password 参数**

```python
# ✅ 正确示例
create_vm_from_template(
    template_name="Ubuntu26.04-LTS",
    vm_name="test-vm",
    vcpu=2,
    ram=4,
    user="ubuntu",        # Linux 模板必需
    password="Pass123"    # Linux 模板必需
)

# ❌ 错误示例（会失败）
create_vm_from_template(
    template_name="Ubuntu26.04-LTS",
    vm_name="test-vm",
    vcpu=2,
    ram=4
    # 缺少 user 和 password - 会返回 "请输入用户名" 错误
)
```

响应模板：
```
我将使用 [模板名称] 创建虚拟机 [虚拟机名称]。
配置：[X] 核 CPU，[Y]GB 内存
用户名：[username]
密码：[password]

[调用 create_vm_from_template]
```

#### 步骤 3: 等待虚拟机创建完成
**必须等待 20 秒**让虚拟机完成初始化。

```
虚拟机创建任务已提交（任务 ID: [task_id]）。
正在等待虚拟机初始化完成...（约需 20 秒）
[等待 20 秒]
```

#### 步骤 4: 获取虚拟机信息和登录凭据
```
现在让我获取虚拟机的详细信息和登录凭据。
[调用 get_vm_info]
```

#### 步骤 5: 提供 SSH 连接信息
从 get_vm_info 的结果中提取信息，告知用户如何连接。

```
✅ 虚拟机已创建并启动成功！

📋 虚拟机信息：
- 名称：[vm_name]
- IP 地址：[ip_address]
- 用户名：[username]
- 密码：[password]
- 状态：[status]

🔐 SSH 连接命令：
ssh [username]@[ip_address]

密码：[password]
```

#### 步骤 6: 测试 SSH 连接（可选）
如果有 SSH MCP 工具，可以测试连接：

```
让我测试 SSH 连接是否正常...
[使用 SSH MCP 工具连接虚拟机]
[执行命令: uname -a]
[执行命令: free -h]

✅ SSH 连接测试成功！虚拟机运行正常。
```

## 关键注意事项

### 1. Linux 模板的必需参数 ⚠️

**Linux 模板（CentOS、Ubuntu、Debian 等）必须提供：**
- `user`: 用户名
- `password`: 密码（至少 8 位）

**常见用户名**：
- Ubuntu: `ubuntu`
- Debian: `debian`
- CentOS/RHEL: `root` 或 `centos`

### 2. 虚拟机名称唯一性

虚拟机名称必须唯一。如果创建失败提示名称已存在：
1. 使用 list_vms 查看现有虚拟机
2. 建议用户使用不同的名称
3. 或询问是否要查看现有虚拟机的信息

### 3. 等待时间

- **创建后必须等待 20 秒**
- 原因：虚拟机需要时间启动并获取 IP 地址
- 不等待的后果：获取不到 IP 地址和完整信息

### 4. 密码安全性

- 自动生成的密码应至少 12 位
- 包含大小写字母、数字和特殊字符
- 不要使用常见密码

### 5. 存储池选择

- 默认情况下不需要指定 `storage_pool_id`
- 只有在磁盘空间不足时才需要手动选择存储池
- 使用 list_storage_pools 查看可用空间

## 完整示例对话

### 示例：创建 Ubuntu 虚拟机

**用户**：帮我创建一个 Ubuntu 虚拟机用于测试

**AI 响应**：
```
好的，我来帮你创建一个 Ubuntu 虚拟机。首先让我查看可用的模板。

[调用 list_templates]

我看到有 Ubuntu26.04-LTS 模板可用。我将创建一个配置如下的虚拟机：
- 模板：Ubuntu26.04-LTS
- 名称：ubuntu-test-vm
- CPU：2 核
- 内存：4 GB
- 用户名：ubuntu
- 密码：Test@2024Secure

[调用 create_vm_from_template，包含所有必需参数]

✅ 虚拟机创建任务已提交（任务 ID: 123）

正在等待虚拟机初始化...（约需 20 秒）

[等待 20 秒]

现在让我获取虚拟机的详细信息。

[调用 get_vm_info]

✅ 虚拟机已创建并启动成功！

📋 虚拟机信息：
- 名称：ubuntu-test-vm
- IP 地址：192.168.1.100
- 用户名：ubuntu
- 密码：Test@2024Secure
- 状态：running
- CPU：2 核
- 内存：4 GB

🔐 SSH 连接命令：
ssh ubuntu@192.168.1.100

密码：Test@2024Secure

虚拟机已准备就绪，可以开始使用了！
```

## 错误处理

### 常见错误及解决方案

| 错误信息 | 原因 | 解决方案 |
|---------|------|----------|
| "请输入用户名" | 缺少 user 参数 | 添加 user 和 password 参数 |
| "磁盘空间不足" | 默认存储池空间不足 | 使用 list_storage_pools 查找有空间的存储池 |
| "虚拟机已存在" | 虚拟机名称重复 | 使用不同的名称或查询现有虚拟机 |
| "模板不存在" | 模板名称错误 | 使用 list_templates 查看正确的模板名称 |

### 空间不足的处理流程

如果创建虚拟机时遇到磁盘空间不足错误：

1. 检查存储池：`[调用 list_storage_pools]`
2. 选择有空间的存储池
3. 使用 `storage_pool_id` 参数重新创建

## 最佳实践

1. ✅ **始终先查询模板**：在创建虚拟机前调用 list_templates
2. ✅ **提供完整参数**：Linux 模板必须包含 user 和 password
3. ✅ **合理等待**：创建后等待 20 秒再查询虚拟机信息
4. ✅ **检查存储空间**：遇到空间问题时使用 list_storage_pools
5. ✅ **生成强密码**：自动生成的密码应足够复杂
6. ✅ **提供 SSH 命令**：帮助用户快速连接虚拟机
7. ✅ **测试连接**：如果可能，使用 SSH 工具测试虚拟机连通性

## 技能触发关键词

- 创建虚拟机
- 查询虚拟机
- VM / KVM
- QVMConsole
- 虚拟机密码
- 模板列表
- 存储池
- SSH 连接
- 虚拟机配置

---

**版本**: 1.0  
**最后更新**: 2026-07-10  
**兼容 MCP 版本**: 0.1.0+
