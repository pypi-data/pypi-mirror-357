from typing import Any, Dict
import os
import requests

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
        api_params = {
            "APIKey": self.api_key,
            "ChinazVer": "1.0",
            "domain": self.model.domain
        }
        response = requests.get(self.base_url, params=api_params, timeout=60)
        return response.json()

def whois_query(domain: str) -> Dict[str, Any]:
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
