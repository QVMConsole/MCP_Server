# 开发者指南

## 项目架构

### 目录结构说明

```
QVMConsole-MCP-Server/
├── src/                    # 源代码目录
│   ├── server.py          # MCP Server 入口，定义工具和处理请求
│   ├── client.py          # QVMConsole API 客户端封装
│   ├── tools.py           # 工具实现，包含业务逻辑
│   ├── config.py          # 配置管理
│   └── __init__.py        # 包初始化
├── config/                # 配置文件目录
│   ├── config.json        # 实际配置（需用户创建）
│   └── config.example.json # 配置模板
├── docs/                  # 文档目录
│   ├── mcp-server-design.md # 设计文档
│   └── usage.md           # 使用文档
├── tests/                 # 测试目录
│   └── test_client.py     # API 客户端测试
└── logs/                  # 日志目录（运行时创建）
```

## 核心模块说明

### 1. config.py - 配置管理

**职责：**
- 加载和验证配置文件
- 提供配置访问接口
- 生成认证请求头

**关键类：**
```python
class Config:
    def __init__(self, config_path: Optional[str] = None)
    def get_auth_headers(self) -> dict
```

**使用方法：**
```python
from config import init_config, get_config

# 初始化配置（通常在 server.py 中）
config = init_config()

# 在其他模块中获取配置
config = get_config()
```

### 2. client.py - API 客户端

**职责：**
- 封装 QVMConsole API 调用
- 处理 HTTP 请求和响应
- 统一错误处理

**关键类：**
```python
class QVMConsoleClient:
    async def list_templates(self) -> List[Dict[str, Any]]
    async def create_vm_from_template(self, params: Dict[str, Any]) -> Dict[str, Any]
    async def get_vm_info(self, vm_name: str) -> Dict[str, Any]
    async def list_vms(self) -> List[Dict[str, Any]]
    async def edit_vm(self, vm_name: str, params: Dict[str, Any]) -> Dict[str, Any]
```

**认证机制：**
```python
# 请求头中包含 API Key
headers = {
    "X-API-Key-ID": api_key_id,
    "X-API-Key": api_key,
    "Content-Type": "application/json"
}
```

### 3. tools.py - 工具实现

**职责：**
- 实现具体的工具逻辑
- 格式化返回结果
- 调用 API 客户端

**关键类：**
```python
class QVMConsoleTools:
    async def list_templates(self) -> str
    async def create_vm_from_template(...) -> str
    async def get_vm_info(vm_name: str, show_password: bool) -> str
    async def list_vms(self) -> str
    async def edit_vm(...) -> str
```

### 4. server.py - MCP Server 入口

**职责：**
- 定义 MCP 工具规范
- 处理工具调用请求
- 启动和管理 MCP Server

**工具定义：**
```python
TOOLS = [
    Tool(
        name="list_templates",
        description="列出所有可用的虚拟机模板...",
        inputSchema={...}
    ),
    # ... 其他工具
]
```

## 添加新工具

### 步骤 1: 在 client.py 中添加 API 方法

```python
async def new_operation(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """新操作的 API 调用"""
    return await self._request("POST", "/api/new/endpoint", json_data=params)
```

### 步骤 2: 在 tools.py 中实现工具逻辑

```python
async def new_tool(self, param1: str, param2: int) -> str:
    """
    新工具的实现
    
    Args:
        param1: 参数说明
        param2: 参数说明
        
    Returns:
        格式化的结果字符串
    """
    try:
        result = await self.client.new_operation({
            "param1": param1,
            "param2": param2
        })
        
        # 格式化返回结果
        response = f"✅ 操作成功\n\n"
        response += f"- 参数1: {param1}\n"
        response += f"- 参数2: {param2}\n"
        
        return response
        
    except QVMConsoleAPIError as e:
        logger.error(f"操作失败: {e}")
        return f"❌ 操作失败: {str(e)}"
```

### 步骤 3: 在 server.py 中注册工具

```python
# 在 TOOLS 列表中添加工具定义
Tool(
    name="new_tool",
    description="新工具的描述",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "参数1的描述"
            },
            "param2": {
                "type": "integer",
                "description": "参数2的描述"
            }
        },
        "required": ["param1", "param2"]
    }
)

# 在 call_tool 函数中添加调用分发
elif name == "new_tool":
    result = await tools.new_tool(
        param1=arguments["param1"],
        param2=arguments["param2"]
    )
```

## 调试技巧

### 1. 启用详细日志

编辑 `config/config.json`：

```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

### 2. 查看实时日志

```bash
# Windows
Get-Content logs\mcp-server.log -Wait

# Linux/macOS
tail -f logs/mcp-server.log
```

### 3. 测试 API 调用

创建测试脚本 `test_api.py`：

```python
import asyncio
from src.config import init_config
from src.client import QVMConsoleClient

async def test():
    init_config()
    client = QVMConsoleClient()
    
    # 测试获取模板列表
    templates = await client.list_templates()
    print(f"获取到 {len(templates)} 个模板")
    
    # 测试获取虚拟机列表
    vms = await client.list_vms()
    print(f"获取到 {len(vms)} 台虚拟机")

if __name__ == "__main__":
    asyncio.run(test())
```

运行测试：
```bash
python test_api.py
```

### 4. 使用 Python 交互式测试

```python
python
>>> import asyncio
>>> from src.config import init_config
>>> from src.tools import QVMConsoleTools
>>> 
>>> init_config()
>>> tools = QVMConsoleTools()
>>> 
>>> # 测试列出模板
>>> result = asyncio.run(tools.list_templates())
>>> print(result)
```

## 错误处理规范

### 1. API 错误

所有 API 错误应该捕获并转换为友好的错误消息：

```python
try:
    result = await self.client.some_operation(params)
    return f"✅ 操作成功: {result}"
except QVMConsoleAPIError as e:
    logger.error(f"操作失败: {e}")
    return f"❌ 操作失败: {str(e)}"
```

### 2. 参数校验

在工具实现中进行必要的参数校验：

```python
async def create_vm_from_template(self, template_name: str, vm_name: str, vcpu: int, ram: int, ...):
    # 参数校验
    if vcpu < 1:
        return "❌ CPU 核心数必须大于 0"
    if ram < 1:
        return "❌ 内存大小必须大于 0"
    
    # 继续处理...
```

### 3. 日志记录

使用不同级别的日志：

```python
from loguru import logger

# 调试信息
logger.debug(f"发送请求: {params}")

# 一般信息
logger.info(f"调用工具: {name}")

# 警告信息
logger.warning(f"参数可能不正确: {value}")

# 错误信息
logger.error(f"操作失败: {error}")

# 异常追踪
logger.exception(f"发生异常")
```

## 性能优化

### 1. 使用异步 I/O

所有 I/O 操作都使用 async/await：

```python
async def get_vm_info(self, vm_name: str):
    # 异步 HTTP 请求
    vm = await self.client.get_vm_info(vm_name)
    return format_vm_info(vm)
```

### 2. 批量操作

对于需要处理多个项目的操作，使用 `asyncio.gather`：

```python
async def get_multiple_vms_info(self, vm_names: List[str]):
    tasks = [self.client.get_vm_info(name) for name in vm_names]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### 3. 连接复用

httpx 客户端自动复用连接，无需额外配置。

## 安全考虑

### 1. API Key 保护

- ✅ 不在代码中硬编码
- ✅ 存储在配置文件中
- ✅ 配置文件不提交到 Git

### 2. 输入验证

对用户输入进行验证，防止注入攻击：

```python
# 虚拟机名称验证
if not re.match(r'^[a-zA-Z0-9_-]+$', vm_name):
    return "❌ 虚拟机名称只能包含字母、数字、下划线和连字符"
```

### 3. 密码处理

虽然 API 返回明文密码，但：
- 只在用户明确请求时显示
- 记录日志时不包含敏感信息

```python
# 日志中不记录密码
logger.info(f"获取虚拟机信息: {vm_name}")  # 不记录返回的密码
```

## 测试指南

### 单元测试

使用 pytest 进行测试：

```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_client.py -v

# 显示详细输出
pytest tests/ -v -s
```

### 集成测试

需要连接到实际的 QVMConsole 实例：

1. 配置测试环境的 API Key
2. 运行测试：`pytest tests/test_client.py`
3. 检查测试结果

## 发布流程

### 1. 更新版本号

编辑以下文件：
- `pyproject.toml` - `version = "0.2.0"`
- `src/__init__.py` - `__version__ = "0.2.0"`
- `config/config.example.json` - `"version": "0.2.0"`

### 2. 更新 CHANGELOG.md

记录新版本的变更：

```markdown
## [0.2.0] - 2026-XX-XX

### 新增功能
- 虚拟机电源操作
- 快照管理

### 修复
- 修复某个 bug
```

### 3. 提交代码

```bash
git add .
git commit -m "Release v0.2.0"
git tag v0.2.0
git push origin main --tags
```

## 常见问题

### Q: 如何支持多个 QVMConsole 实例？

A: 当前版本每个 MCP Server 对应一个 QVMConsole 实例。如需支持多个实例，可以：
1. 启动多个 MCP Server 进程
2. 每个进程使用不同的配置文件

### Q: 如何扩展支持新的 QVMConsole API？

A: 按照"添加新工具"部分的步骤操作。

### Q: 如何处理 API 版本兼容性？

A: 当前通过 API 响应字段判断，后续可以添加版本检查机制。

## 代码规范

- 使用中文注释
- 函数和类都要有 docstring
- 遵循 PEP 8 代码风格
- 使用类型提示（Type Hints）
- 错误消息使用中文

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 联系方式

- QVMConsole 项目：https://www.qvmconsole.cn/
- 提交 Issue：（GitHub 仓库地址）
