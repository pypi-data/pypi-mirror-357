from typing import Any, Dict
import os
import requests
import logging

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 检查环境变量
API_KEY = os.getenv("CHINAZ_API_KEY")
if not API_KEY:
    logger.warning("CHINAZ_API_KEY 环境变量未设置")

WHOIS_API_URL = 'https://openapi.chinaz.net/v1/1001/whois'

class DomainModel:
    """域名模型类"""
    def __init__(self, domain: str):
        if not domain:
            raise ValueError("域名不能为空")
        self.domain = domain

class WhoisContext:
    """WHOIS 查询上下文"""
    def __init__(self, model: DomainModel, api_key: str = None):
        if not model:
            raise ValueError("DomainModel 不能为空")
        self.model = model
        self.api_key = api_key or API_KEY
        if not self.api_key:
            raise ValueError("API Key 不能为空")
        self.base_url = WHOIS_API_URL

    def get_whois_info(self) -> Dict[str, Any]:
        try:
            logger.debug(f"正在查询域名: {self.model.domain}")
            api_params = {
                "APIKey": self.api_key,
                "ChinazVer": "1.0",
                "domain": self.model.domain
            }
            response = requests.get(self.base_url, params=api_params, timeout=60)
            response.raise_for_status()  # 检查响应状态
            result = response.json()
            logger.debug(f"查询结果: {result}")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"API 请求失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"查询失败: {str(e)}")
            raise

def whois_query(domain: str) -> Dict[str, Any]:
    try:
        if not domain:
            raise ValueError("domain参数不能为空")
        if not API_KEY:
            raise ValueError("Missing CHINAZ API Key")
        
        logger.info(f"开始查询域名: {domain}")
        domain_model = DomainModel(domain)
        whois_context = WhoisContext(domain_model)
        result = whois_context.get_whois_info()
        
        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"查询失败: {str(e)}", exc_info=True)
        return {
            "code": -1,
            "message": str(e),
            "data": None
        }
