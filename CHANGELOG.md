# QVMConsole MCP Server - 更新日志

## 更新日志

## [未发布]

### 新增

- **新增 `list_storage_pools` 工具**：列出所有存储池及其可用空间信息
- **增强 `create_vm_from_template` 工具**：添加 `storage_pool_id` 参数支持，可以指定虚拟机存储位置
- **新增网卡配置参数**：
  - `nic_model`：网卡模型（virtio/e1000e/rtl8139）
  - `switch_id`：VPC 交换机 ID，用于 VPC 网络配置
  - `security_group_id`：安全组 ID，用于防火墙规则配置

### 改进

- **解决磁盘空间不足问题**：当默认存储池空间不足时，可以选择其他有足够空间的存储池
- **增强网络配置能力**：支持自定义网卡模型和 VPC 网络配置
- **移除 `node_id` 参数**：用更标准的 `storage_pool_id` 参数替代

### 文档

- 添加存储池功能测试脚本：`tests/test_storage_pool.py`
- 更新问题分析报告：`ANALYSIS_DISK_SPACE_ISSUE.md`
- 添加存储空间检查脚本：`tests/check_storage.py`
- 创建 Skill 技能文档：`skill/qvmconsole-vm-management/SKILL.md`
- 添加网卡配置说明到 Skill 文档

### 修复

- 修复创建虚拟机时无法选择存储位置的问题
- 修复测试脚本缺少必需参数（user 和 password）的问题

---

## [1.0.0] - 2026-07-10

### 新增功能

- ✨ 基础 MCP Server 实现
- ✨ 支持 API Key 认证方式
- ✨ 实现 5 个核心工具：
  - `list_templates` - 列出虚拟机模板
  - `create_vm_from_template` - 从模板创建虚拟机
  - `get_vm_info` - 获取虚拟机详情（包括密码）
  - `list_vms` - 列出所有虚拟机
  - `edit_vm` - 编辑虚拟机配置
- 📝 完整的文档和使用说明
- 🧪 基础测试用例

### 技术细节

- Python 3.10+ 支持
- 基于官方 MCP SDK
- 使用 httpx 进行异步 HTTP 请求
- 集成 loguru 日志系统
- JSON 配置文件管理

## [未来计划]

### v0.2.0 (计划中)
- 虚拟机电源操作（启动、关机、重启、强制断电）
- 快照管理（创建、恢复、删除）
- 任务状态查询
- VNC 控制台访问信息获取

### v0.3.0 (计划中)
- 磁盘管理（添加、调整大小、删除）
- 网络管理（端口转发、静态 IP）
- 虚拟机删除功能
- 批量操作支持

### v0.4.0 (计划中)
- 模板管理（创建、导入、导出）
- 用户配额查询
- 监控统计数据
- WebSocket 实时通知支持
