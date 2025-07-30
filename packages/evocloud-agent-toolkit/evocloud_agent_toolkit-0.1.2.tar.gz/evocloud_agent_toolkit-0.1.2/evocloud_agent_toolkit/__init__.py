"""
EvoCloud Agent Toolkit

A comprehensive Python SDK for integrating EvoCloud payment services with AI agents and applications.

This toolkit provides:
- LangChain tools for building conversational payment experiences
- MCP (Model Context Protocol) tools for model integration
- Direct SDK interfaces for custom applications

Usage:
    from evocloud_agent_toolkit import EvoCloudSDK
    
    # Initialize the SDK
    sdk = EvoCloudSDK(
        base_url="https://api.evocloud.com",
        sign_key="your_sign_key",
        sid="your_sid"
    )
    
    # Use LangChain tools
    langchain_tools = sdk.get_langchain_tools()
    
    # Use direct methods
    order_id = sdk.generate_order_id("PAYMENT")
    result = sdk.create_linkpay_order(order_id, "USD", "99.99")
"""

from .langchain import EvoCloudToolkit, EvoCloudLinkPayTool

__version__ = "0.1.0"
__author__ = "EvoCloud SDK Team"
__description__ = "EvoCloud Agent Toolkit - Python SDK for AI-powered payment integration"

__all__ = [
    "EvoCloudToolkit", 
    "EvoCloudLinkPayTool"
]