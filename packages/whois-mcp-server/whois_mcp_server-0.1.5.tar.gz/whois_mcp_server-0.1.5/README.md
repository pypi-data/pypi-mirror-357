# WHOIS MCP Server

[![PyPI version](https://badge.fury.io/py/whois-mcp-server.svg)](https://badge.fury.io/py/whois-mcp-server)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个基于 Python 和模型上下文协议（MCP）实现的 WHOIS 查询服务器。提供 MCP 工具来查询域名的 WHOIS 信息。

## 功能特点

- 🌐 域名 WHOIS 信息查询
- 🔧 基于 FastMCP 框架
- 📡 支持 Chinaz API 接口
- 🛡️ 内置输入验证和错误处理
- 🚀 支持多种传输协议（stdio/sse）

## 快速开始

### 安装

```bash
pip install whois-mcp-server
```

### 使用

#### 命令行方式

```bash
# 启动 MCP 服务器
whois-mcp-server
```

#### Python 代码方式

```python
from whois_mcp.__main__ import whois_query

# 查询域名 WHOIS 信息
result = whois_query("example.com")
print(result)
```

## MCP 工具文档

### whois_query

查询指定域名的 WHOIS 信息。

#### 参数

- `domain` (str): 要查询的域名，如 "example.com"

#### 返回格式

```json
{
  "code": 0,
  "message": "success",
  "data": {
    // WHOIS 查询结果
  }
}
```

#### 使用示例

```python
from whois_mcp.__main__ import whois_query

# 查询 qq.com 的 WHOIS 信息
result = whois_query("qq.com")
if result["code"] == 0:
    print("查询成功:", result["data"])
else:
    print("查询失败:", result["message"])
```

## 环境配置

### API Key 设置

设置 Chinaz API Key 环境变量：

```bash
export TAVILY_API_KEY="your_api_key_here"
```

或在 Windows 中：

```cmd
set TAVILY_API_KEY=your_api_key_here
```

## MCP 服务器配置

### 在 Claude Desktop 中配置

修改您的 `claude-desktop-config.json` 文件：

```json
{
  "mcpServers": {
    "whoismcp": {
      "command": "whois-mcp-server"
    }
  }
}
```

### 使用 uvx 运行

```json
{
  "mcpServers": {
    "whoismcp": {
      "command": "uvx",
      "args": ["whois-mcp-server"]
    }
  }
}
```

## 开发

### 从源码安装

```bash
git clone https://github.com/your-username/whois-mcp-server.git
cd whois-mcp-server
pip install -e .
```

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black whois_mcp/
flake8 whois_mcp/
```

## 项目结构

```
whois-mcp-server/
├── whois_mcp/
│   ├── __init__.py
│   └── __main__.py
├── tests/
│   ├── __init__.py
│   └── test_whois.py
├── pyproject.toml
├── MANIFEST.in
├── LICENSE
└── README.md
```

## 依赖项

- Python 3.8+
- requests>=2.25.0
- mcp>=1.0.0
- fastmcp>=0.1.0

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 贡献

欢迎提交 Pull Requests 和 Issues！

在提交代码前，请确保：

1. 代码符合 PEP 8 规范
2. 添加适当的测试用例
3. 更新相关文档

## 支持

如有问题，请通过 [GitHub Issues](https://github.com/your-username/whois-mcp-server/issues) 提交。
