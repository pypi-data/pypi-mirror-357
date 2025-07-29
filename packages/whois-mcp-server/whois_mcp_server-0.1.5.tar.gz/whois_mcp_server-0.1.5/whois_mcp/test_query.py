from whois_mcp.whois_api import whois_query
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_whois_query():
    try:
        logger.info("开始测试 whois 查询...")
        result = whois_query("qq.com")
        logger.info(f"查询结果: {result}")
        return result
    except Exception as e:
        logger.error(f"测试失败: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    test_whois_query() 