import pytest
from whois_mcp.__main__ import whois_query, DomainModel, WhoisContext


def test_domain_model():
    """测试域名模型"""
    domain = "example.com"
    model = DomainModel(domain)
    assert model.domain == domain


def test_whois_context():
    """测试WHOIS上下文"""
    domain = "example.com"
    model = DomainModel(domain)
    context = WhoisContext(model)
    assert context.model.domain == domain
    assert context.base_url == 'https://openapi.chinaz.net/v1/1001/whois'


def test_whois_query_empty_domain():
    """测试空域名参数"""
    result = whois_query("")
    assert result["code"] == -1
    assert "domain参数不能为空" in result["message"]


def test_whois_query_none_domain():
    """测试None域名参数"""
    result = whois_query(None)
    assert result["code"] == -1
    assert "domain参数不能为空" in result["message"]


if __name__ == "__main__":
    pytest.main([__file__]) 