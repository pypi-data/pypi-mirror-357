from mcp.server.fastmcp import FastMCP
from whois_mcp.whois_api import whois_query

# MCP 实例
mcp = FastMCP("whois-mcp-server")

@mcp.tool()
def mcp_whois_query(domain: str):
    return whois_query(domain)

def main():
    mcp.run(transport='sse')

if __name__ == "__main__":
    main()