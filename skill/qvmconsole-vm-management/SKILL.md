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
- 用户需要控制虚拟机电源（启动、关机、重启等）
- 用户需要管理虚拟机快照（创建、恢复、删除）
- 用户需要设置虚拟机定时任务
- 用户需要查看虚拟机监控数据
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
列出虚拟机可用的存储位置及其可用空间信息。

**使用场景**：检查存储空间是否充足，选择合适的存储位置创建虚拟机

**示例**：
```
请查看可用的存储位置
显示虚拟机存储空间使用情况
```

**返回信息**：
- 存储位置 ID（用于 `storage_pool_id` 参数）
- 存储目录路径
- 总容量、已使用、可用空间
- 是否为默认存储位置
- 启用状态

### 3. list_switches
列出所有 VPC 交换机。

**使用场景**：查看可用的交换机 ID，用于创建虚拟机时配置网络

**示例**：
```
请列出所有交换机
```

**返回信息**：
- 交换机 ID（用于 `switch_id` 参数）
- 交换机名称
- 网桥配置
- 是否为默认交换机
- 使用建议和示例代码

### 4. create_vm_from_template
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
- `nic_model`: 网卡模型（virtio/e1000e/rtl8139）
- `switch_id`: VPC 交换机 ID（**如需网络则必需**，通常为 1 或 2）
- `security_group_id`: 安全组 ID（用于防火墙规则）

**⚠️ 网络注意事项**：
- 如果需要虚拟机有网络连接，**必须指定 `switch_id`**（通常为 1）
- 只指定 `nic_model` 而不指定 `switch_id`，虚拟机将没有网卡

**示例**：
```
使用 Ubuntu26.04-LTS 模板创建一个名为 test-vm 的虚拟机，配置 2 核 CPU 和 4GB 内存
```

### 5. get_vm_info
获取虚拟机详细信息，包括登录密码。

**必需参数**：
- `vm_name`: 虚拟机名称

**示例**：
```
查看 test-vm 虚拟机的详细信息和密码
```

### 6. list_vms
列出所有虚拟机及其状态。

### 7. edit_vm
编辑虚拟机配置。

### 8. add_disk
为虚拟机添加新的数据硬盘。

**必需参数**：
- `vm_name`: 虚拟机名称
- `size_gb`: 磁盘大小（GB）

**可选参数**：
- `format`: 磁盘格式（qcow2/raw，默认 qcow2）
- `bus`: 磁盘总线（virtio/scsi/sata/ide，默认 virtio）

**磁盘格式说明**：
- `qcow2`: 推荐，支持快照和压缩
- `raw`: 性能更好，但占用空间更多

**示例**：
```
为虚拟机 test-vm 添加一个 100GB 的数据盘
给 test-vm 增加 50GB 硬盘
```

### 9. list_disks
列出虚拟机的所有磁盘信息。

**必需参数**：
- `vm_name`: 虚拟机名称

### 10. resize_disk
扩容虚拟机磁盘（只能扩大，不能缩小）。

**必需参数**：
- `vm_name`: 虚拟机名称
- `dev`: 设备名称（如 vda, vdb）
- `size_gb`: 新的磁盘大小（GB）

**示例**：
```
将 test-vm 的 vdb 磁盘扩容到 200GB
```

### 11. vm_power_operation
虚拟机电源操作。

**必需参数**：
- `vm_name`: 虚拟机名称
- `action`: 操作类型（start/shutdown/destroy/reboot/reset）

**操作类型说明**：
- `start`: 启动虚拟机
- `shutdown`: 正常关机（需要虚拟机支持 ACPI）
- `destroy`: 强制关机（相当于拔电源）
- `reboot`: 重启虚拟机
- `reset`: 重置虚拟机（硬重启）

**示例**：
```
启动虚拟机 test-vm
关闭虚拟机 test-vm
重启虚拟机 test-vm
```

### 12. list_snapshots
列出虚拟机的所有快照及配额信息。

**必需参数**：
- `vm_name`: 虚拟机名称

### 13. create_snapshot
创建虚拟机快照。

**必需参数**：
- `vm_name`: 虚拟机名称
- `snapshot_name`: 快照名称

**可选参数**：
- `description`: 快照描述
- `include_memory`: 是否包含内存状态（默认 false）
- `auto_fix_nvram`: 自动修复 UEFI NVRAM（UEFI 虚拟机需要，默认 false）

**示例**：
```
为虚拟机 test-vm 创建一个名为 backup-20260710 的快照
创建包含内存状态的快照
```

### 14. revert_snapshot
恢复虚拟机到指定快照的状态。

**警告**：这将丢失快照之后的所有数据变更。

**必需参数**：
- `vm_name`: 虚拟机名称
- `snapshot_name`: 快照名称

### 15. delete_snapshot
删除虚拟机快照。

**必需参数**：
- `vm_name`: 虚拟机名称
- `snapshot_name`: 快照名称

### 16. list_vm_schedules
列出虚拟机的所有定时任务。

**必需参数**：
- `vm_name`: 虚拟机名称

### 17. create_vm_schedule
创建虚拟机定时任务。

**必需参数**：
- `vm_name`: 虚拟机名称
- `action`: 操作类型（start/shutdown/delete）
- `schedule_type`: 计划类型（once/daily/weekly）

**可选参数**：
- `time_of_day`: 每日执行时间，格式 HH:MM（daily 和 weekly 必填）
- `run_at`: 一次性执行时间，格式 YYYY-MM-DD HH:MM:SS（once 必填）
- `weekdays`: 星期几执行，1-7 表示周一到周日（weekly 必填）
- `enabled`: 是否启用（默认 true）
- `timezone`: 时区（默认 Asia/Shanghai）

**操作类型说明**：
- `start`: 定时启动虚拟机
- `shutdown`: 定时关机
- `delete`: 定时删除虚拟机（仅支持 once 类型）

**计划类型说明**：
- `once`: 一次性执行（需要指定 run_at）
- `daily`: 每日执行（需要指定 time_of_day）
- `weekly`: 每周执行（需要指定 time_of_day 和 weekdays）

**示例**：
```
# 每天凌晨2点自动关机
create_vm_schedule(
    vm_name="test-vm",
    action="shutdown",
    schedule_type="daily",
    time_of_day="02:00"
)

# 每周一、三、五早上8点自动启动
create_vm_schedule(
    vm_name="test-vm",
    action="start",
    schedule_type="weekly",
    time_of_day="08:00",
    weekdays=[1, 3, 5]
)

# 2024年12月31日晚上11点删除虚拟机
create_vm_schedule(
    vm_name="test-vm",
    action="delete",
    schedule_type="once",
    run_at="2024-12-31 23:00:00"
)
```

### 18. delete_vm_schedule
删除虚拟机定时任务。

**必需参数**：
- `vm_name`: 虚拟机名称
- `schedule_id`: 定时任务 ID

### 19. get_vm_stats
获取虚拟机实时监控数据。

**必需参数**：
- `vm_name`: 虚拟机名称

**返回信息**：
- CPU 使用率
- 内存使用情况
- 磁盘 I/O 数据
- 网络流量统计

**示例**：
```
查看虚拟机 test-vm 的监控数据
显示虚拟机 test-vm 的 CPU 和内存使用情况
```

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
**⚠️ 关键：如需网络必须提供 switch_id 参数（通常为 1）**

```python
# ✅ 正确示例（有网络）
create_vm_from_template(
    template_name="Ubuntu26.04-LTS",
    vm_name="test-vm",
    vcpu=2,
    ram=4,
    user="ubuntu",        # Linux 模板必需
    password="Pass123",   # Linux 模板必需
    switch_id=1           # 网络必需（使用"基础网络"交换机）
)

# ❌ 错误示例 1（会失败：缺少用户名）
create_vm_from_template(
    template_name="Ubuntu26.04-LTS",
    vm_name="test-vm",
    vcpu=2,
    ram=4
    # 缺少 user 和 password - 会返回 "请输入用户名" 错误
)

# ❌ 错误示例 2（虚拟机没有网卡）
create_vm_from_template(
    template_name="Ubuntu26.04-LTS",
    vm_name="test-vm",
    vcpu=2,
    ram=4,
    user="ubuntu",
    password="Pass123"
    # 缺少 switch_id - 虚拟机将没有网卡，无法联网
)
```

响应模板：
```
我将使用 [模板名称] 创建虚拟机 [虚拟机名称]。
配置：[X] 核 CPU，[Y]GB 内存
用户名：[username]
密码：[password]
网络：使用基础网络交换机（switch_id: 1）

[调用 create_vm_from_template，必须包含 user、password 和 switch_id]
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

- 默认情况下不需要指定 `storage_pool_id`，系统会使用默认存储位置
- 只有在默认存储位置空间不足时才需要手动选择其他存储位置
- 使用 list_storage_pools 查看可用的存储位置及其可用空间
- 选择有足够空间且状态为"可用"的存储位置

### 6. 网卡配置 ⚠️

**重要：创建有网络连接的虚拟机必须同时指定 `nic_model` 和 `switch_id`**

**网卡模型 (`nic_model`)**：
- `virtio`：推荐，性能最好（默认）
- `e1000e`：Intel E1000e，兼容性好
- `rtl8139`：Realtek RTL8139，旧系统兼容

**VPC 交换机 (`switch_id`)** - **必需参数（如果需要网络）**：
- 如果 `switch_id` 为 0 或不传，虚拟机将**没有网卡**（`--network none`）
- 必须指定有效的交换机 ID（通常是 1 或 2）才能创建有网络的虚拟机
- 常见交换机：
  - ID: 1 - 基础网络
  - ID: 2 - default

**安全组 (`security_group_id`)**：
- 指定安全组，配置防火墙规则（可选）

**如何查询可用交换机**：
```bash
# 运行查询脚本
python tests/check_switches.py
```

**正确示例（有网卡）**：
```python
# ✅ 正确：指定了 switch_id，虚拟机有网卡
create_vm_from_template(
    template_name="Ubuntu26.04-LTS",
    vm_name="test-vm",
    vcpu=2,
    ram=4,
    user="ubuntu",
    password="Pass123",
    nic_model="virtio",        # 网卡模型
    switch_id=1                # ← 必需！使用"基础网络"交换机
)
```

**错误示例（无网卡）**：
```python
# ❌ 错误：只有 nic_model 没有 switch_id，虚拟机没有网卡
create_vm_from_template(
    template_name="Ubuntu26.04-LTS",
    vm_name="test-vm",
    vcpu=2,
    ram=4,
    user="ubuntu",
    password="Pass123",
    nic_model="virtio"  # 只有这个参数不够！
    # 缺少 switch_id - 虚拟机将没有网卡
)

# ❌ 错误：switch_id 为 0，虚拟机没有网卡
create_vm_from_template(
    template_name="Ubuntu26.04-LTS",
    vm_name="test-vm",
    vcpu=2,
    ram=4,
    user="ubuntu",
    password="Pass123",
    nic_model="virtio",
    switch_id=0  # ← 0 表示不创建网卡
)
```

## 完整示例对话

### 示例：创建 Ubuntu 虚拟机

**用户**：帮我创建一个 Ubuntu 虚拟机用于测试

**AI 响应**：
```
好的，我来帮你创建一个 Ubuntu 虚拟机。首先让我查看可用的模板和交换机。

[调用 list_templates]
[调用 list_switches]

我看到有 Ubuntu26.04-LTS 模板可用。我将创建一个配置如下的虚拟机：
- 模板：Ubuntu26.04-LTS
- 名称：ubuntu-test-vm
- CPU：2 核
- 内存：4 GB
- 用户名：ubuntu
- 密码：Test@2024Secure
- 网络：基础网络（switch_id: 1）

[调用 create_vm_from_template，包含 user、password 和 switch_id]

✅ 虚拟机创建任务已提交（任务 ID: 123）

正在等待虚拟机初始化...（约需 20 秒）

[等待 60 秒]

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
| "磁盘空间不足" | 默认存储位置空间不足 | 使用 list_storage_pools 查找有空间的存储位置 |
| "虚拟机已存在" | 虚拟机名称重复 | 使用不同的名称或查询现有虚拟机 |
| "模板不存在" | 模板名称错误 | 使用 list_templates 查看正确的模板名称 |
| 虚拟机没有网卡 | 未指定 switch_id | 添加 switch_id 参数（通常为 1） |

### 空间不足的处理流程

如果创建虚拟机时遇到磁盘空间不足错误：

1. 检查存储位置：`[调用 list_storage_pools]`
2. 选择有足够空间且状态为"可用"的存储位置
3. 使用 `storage_pool_id` 参数重新创建

## 最佳实践

1. ✅ **始终先查询模板和交换机**：在创建虚拟机前调用 list_templates 和 list_switches
2. ✅ **提供完整参数**：Linux 模板必须包含 user 和 password
3. ✅ **配置网络连接**：需要网络的虚拟机必须指定 switch_id（通常为 1）
4. ✅ **合理等待**：创建后等待 20 秒再查询虚拟机信息
5. ✅ **检查存储空间**：遇到空间问题时使用 list_storage_pools
6. ✅ **生成强密码**：自动生成的密码应足够复杂
7. ✅ **提供 SSH 命令**：帮助用户快速连接虚拟机
8. ✅ **测试连接**：如果可能，使用 SSH 工具测试虚拟机连通性

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
- 启动/关机/重启虚拟机
- 虚拟机快照
- 定时任务
- 虚拟机监控
- CPU/内存使用率
- 添加硬盘/扩容磁盘

---

**版本**: 2.3  
**最后更新**: 2026-07-10  
**兼容 MCP 版本**: 0.1.0+

## 更新日志

### v2.3 (2026-07-10)
- ✅ 新增磁盘管理功能（添加/列出/扩容硬盘）
- 📝 完善磁盘管理相关文档
- ⚠️ 出于安全考虑，不提供删除磁盘功能

### v2.2 (2026-07-10)
- 🔧 修复存储池API问题（使用 `/api/storage-pool/vm-targets` 获取虚拟机可用存储位置）
- 📝 更新存储池相关文档说明

### v2.1 (2026-07-10)
- 🔧 修复定时任务创建问题（使用正确的API参数结构）
- 📝 更新定时任务文档说明（使用 schedule_type 代替 cron_expr）

### v2.0 (2026-07-10)
- ✅ 修复存储池列表显示问题（正确解析字节单位和状态）
- ✅ 新增虚拟机电源操作功能（启动/关机/重启/强制关机/重置）
- ✅ 新增快照管理功能（创建/恢复/删除快照，支持内存快照）
- ✅ 新增虚拟机定时任务功能（支持定时启动、关机、删除）
- ✅ 新增虚拟机监控数据获取功能（CPU、内存、磁盘I/O、网络流量）

### v1.0 (初始版本)
- 基础虚拟机管理功能
- 模板列表查询
- 虚拟机创建和编辑
- 存储池和交换机查询
