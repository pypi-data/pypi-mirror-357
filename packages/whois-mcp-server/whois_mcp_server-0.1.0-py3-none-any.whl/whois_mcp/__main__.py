#!/usr/bin/env python3
"""
WHOIS MCP Server 主入口
"""

import sys
import os

def main():
    """主函数入口点"""
    try:
        # 尝试导入 MCP 服务器
        from .mcp_server import main as mcp_main
        mcp_main()
    except ImportError as e:
        print("❌ 缺少必要的依赖包")
        print("请安装依赖: pip install mcp fastmcp")
        print(f"错误详情: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 