from whois_mcp.whois_api import whois_query

if __name__ == "__main__":
    result = whois_query("qq.com")
    print(result) 