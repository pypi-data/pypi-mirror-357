"""
EvoCloud LangChain Toolkit

This module provides the main toolkit for EvoCloud payment services.
"""

import os
from typing import Optional

from pydantic import Field, PrivateAttr
from langchain_core.tools import BaseToolkit
from evocloud_sdk.common import SignType
from .linkpay_tool import EvoCloudLinkPayTool


class EvoCloudToolkit(BaseToolkit):
    """EvoCloud LangChain 工具包"""
    
    _linkpay_tool: Optional[EvoCloudLinkPayTool] = PrivateAttr(default=None)

    def __init__(
        self, 
        base_url: Optional[str] = None,
        sign_key: Optional[str] = None,
        sid: Optional[str] = None,
        sign_type: SignType = SignType.SHA256,
        timeout: int = 60,
        max_retries: int = 0,
        webhook_url: Optional[str] = None
    ):
        """
        初始化 EvoCloud 工具包
        
        Args:
            base_url: EVO Cloud API 基础URL，默认从环境变量 EVOCLOUD_BASE_URL 读取
            sign_key: 签名密钥，默认从环境变量 EVOCLOUD_SIGN_KEY 读取
            sid: 系统ID，默认从环境变量 EVOCLOUD_SID 读取
            sign_type: 签名算法类型，默认 SHA256
            timeout: 请求超时时间（秒），默认 60
            max_retries: 最大重试次数，默认 1
            webhook_url: 默认回调地址，可选，默认从环境变量 EVOCLOUD_WEBHOOK_URL 读取
        """
        # 从环境变量或参数获取配置
        base_url = base_url if base_url else os.getenv("EVOCLOUD_BASE_URL")
        sign_key = sign_key if sign_key else os.getenv("EVOCLOUD_SIGN_KEY")
        sid = sid if sid else os.getenv("EVOCLOUD_SID")
        sign_type = sign_type
        timeout = timeout
        max_retries = max_retries
        webhook_url = webhook_url if webhook_url else os.getenv("EVOCLOUD_WEBHOOK_URL")
        
        # 验证必要参数
        if not base_url:
            raise ValueError("base_url is required. Set EVOCLOUD_BASE_URL environment variable or pass base_url parameter.")
        if not sign_key:
            raise ValueError("sign_key is required. Set EVOCLOUD_SIGN_KEY environment variable or pass sign_key parameter.")
        if not sid:
            raise ValueError("sid is required. Set EVOCLOUD_SID environment variable or pass sid parameter.")
        
        # 创建 LinkPay 工具（内部会创建 EVOCloudClient）
        self._linkpay_tool = EvoCloudLinkPayTool(
            base_url=base_url,
            sid=sid,
            sign_key=sign_key,
            webhook_url=webhook_url
        )

    def get_tools(self):
        """获取所有可用工具"""
        return self._linkpay_tool.get_tools()