from mcp.server.fastmcp import FastMCP
from whois_mcp.whois_api import whois_query
import socket
import logging

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# MCP 实例
mcp = FastMCP("whois-mcp-server")

@mcp.tool()
def mcp_whois_query(domain: str):
    logger.debug(f"Querying whois for domain: {domain}")
    return whois_query(domain)



def main():
    try:
        mcp.run(transport='sse', port=18895)
    except Exception as e:
        logger.error(f"服务启动失败: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()