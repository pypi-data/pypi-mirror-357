"""
WHOIS MCP Server

A WHOIS MCP server for domain availability checking.
"""

__version__ = "0.1.4"
__author__ = "ahooop"
__email__ = "ahooop@163.com"

from .whois_api import whois_query, DomainModel, WhoisContext

__all__ = ["whois_query", "DomainModel", "WhoisContext"]
