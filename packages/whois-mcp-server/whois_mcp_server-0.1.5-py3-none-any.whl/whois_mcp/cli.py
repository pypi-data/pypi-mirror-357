import argparse
import logging
from .whois_api import whois_query

def main():
    # 设置日志
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # 创建参数解析器
    parser = argparse.ArgumentParser(description='WHOIS 查询工具')
    parser.add_argument('domain', help='要查询的域名')
    args = parser.parse_args()

    try:
        # 执行查询
        logger.info(f"开始查询域名: {args.domain}")
        result = whois_query(args.domain)
        logger.info(f"查询结果: {result}")
    except Exception as e:
        logger.error(f"查询失败: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    main() 