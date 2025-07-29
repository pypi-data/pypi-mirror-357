#!/usr/bin/env python3
"""
WHOIS MCP Server
基于 FastMCP 框架的 WHOIS 查询服务器
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional
from fastmcp import FastMCP, Tool
from fastmcp.models import ToolCall, ToolResult
import requests

# 获取 API Key
API_KEY = os.getenv("TAVILY_API_KEY")

class WhoisMCPServer(FastMCP):
    """WHOIS MCP 服务器"""
    
    def __init__(self):
        super().__init__(
            name="whois-mcp-server",
            version="0.1.0",
            description="A WHOIS MCP server for domain availability checking"
        )
        
        # 注册工具
        self.register_tool(
            Tool(
                name="whois_query",
                description="查询指定域名的 WHOIS 信息",
                input_schema={
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "description": "要查询的域名，如 'example.com'"
                        }
                    },
                    "required": ["domain"]
                }
            ),
            self.whois_query_tool
        )
    
    async def whois_query_tool(self, call: ToolCall) -> ToolResult:
        """WHOIS 查询工具"""
        try:
            # 获取参数
            domain = call.args.get("domain")
            
            if not domain:
                return ToolResult(
                    content="domain参数不能为空",
                    is_error=True
                )
            
            if not API_KEY:
                return ToolResult(
                    content="Missing API Key. Please set TAVILY_API_KEY environment variable.",
                    is_error=True
                )
            
            # 调用 WHOIS API
            result = await self._query_whois(domain)
            
            return ToolResult(
                content=json.dumps(result, ensure_ascii=False, indent=2)
            )
            
        except Exception as e:
            return ToolResult(
                content=f"查询失败: {str(e)}",
                is_error=True
            )
    
    async def _query_whois(self, domain: str) -> Dict[str, Any]:
        """查询 WHOIS 信息"""
        api_params = {
            "APIKey": API_KEY,
            "ChinazVer": "1.0",
            "domain": domain
        }
        
        # 使用异步请求
        async with asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: requests.get(
                'https://openapi.chinaz.net/v1/1001/whois',
                params=api_params,
                timeout=60
            )
        ) as response:
            return response.json()

def main():
    """主函数"""
    server = WhoisMCPServer()
    
    # 启动服务器
    print("🚀 启动 WHOIS MCP Server...")
    print(f"API Key: {'已设置' if API_KEY else '未设置'}")
    
    # 运行服务器
    server.run()

if __name__ == "__main__":
    main() 