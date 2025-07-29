from typing import Any, Dict
import os
import requests
from mcp.server.fastmcp import FastMCP

# MCP 实例
mcp = FastMCP("whois-mcp-server")

API_KEY = os.getenv("TAVILY_API_KEY")
WHOIS_API_URL = 'https://openapi.chinaz.net/v1/1001/whois'

class DomainModel:
    """域名模型类"""
    def __init__(self, domain: str):
        self.domain = domain

class WhoisContext:
    """WHOIS 查询上下文"""
    def __init__(self, model: DomainModel, api_key: str = None):
        self.model = model
        self.api_key = api_key or API_KEY
        self.base_url = WHOIS_API_URL

    def get_whois_info(self) -> Dict[str, Any]:
        """获取 WHOIS 信息"""
        api_params = {
            "APIKey": self.api_key,
            "ChinazVer": "1.0",
            "domain": self.model.domain
        }
        response = requests.get(self.base_url, params=api_params, timeout=60)
        return response.json()

def do_whois_query(domain: str) -> Dict[str, Any]:
    """whois 查询主逻辑，返回 dict"""
    if not domain:
        return {
            "code": -1,
            "message": "domain参数不能为空",
            "data": None
        }
    if not API_KEY:
        return {
            "code": -1,
            "message": "Missing API Key",
            "data": None
        }
    domain_model = DomainModel(domain)
    whois_context = WhoisContext(domain_model)
    result = whois_context.get_whois_info()
    return {
        "code": 0,
        "message": "success",
        "data": result
    }

@mcp.tool()
def whois_query(domain: str) -> Dict[str, Any]:
    """Whois 查询接口
    Args:
        domain: 域名字符串，如 'qq.com'
    Returns:
        dict: 查询结果，包含 code/message/data
    """
    try:
        return do_whois_query(domain)
    except Exception as ex:
        return {
            "code": -1,
            "message": f"系统异常：{str(ex)}",
            "data": None
        }

if __name__ == "__main__":
    mcp.run(transport='sse')