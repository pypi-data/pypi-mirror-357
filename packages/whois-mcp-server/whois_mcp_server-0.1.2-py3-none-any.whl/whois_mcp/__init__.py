"""
WHOIS MCP Server

A WHOIS MCP server for domain availability checking.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .whois_api import whois_query, DomainModel, WhoisContext

__all__ = ["whois_query", "DomainModel", "WhoisContext"]
