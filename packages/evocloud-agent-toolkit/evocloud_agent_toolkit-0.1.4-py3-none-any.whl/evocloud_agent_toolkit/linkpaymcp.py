import sys
import os
from typing import Optional, List
from mcp.server.fastmcp import FastMCP
from .langchain.linkpay_tool import EvoCloudLinkPayTool

# Create MCP server
mcp = FastMCP("EvoCloud LinkPay Server", host="0.0.0.0",
              port=os.getenv("LINKPAY_MCP_PORT", 8080),
              debug=os.getenv("LINKPAY_MCP_DEBUG", False))

# LinkPay tool instance will be created lazily
linkpay_tool = None


def get_linkpay_tool():
    """Get or create LinkPay tool instance"""
    global linkpay_tool
    if linkpay_tool is None:
        base_url = os.getenv("EVOCLOUD_BASE_URL")
        sid = os.getenv("EVOCLOUD_SID")
        webhook_url = os.getenv("EVOCLOUD_WEBHOOK_URL")
        linkpay_tool = EvoCloudLinkPayTool(base_url=base_url, sid=sid, webhook_url=webhook_url)
    return linkpay_tool


@mcp.tool()
def generate_merchant_order_id(prefix: str = "LINKPAY") -> str:
    """生成唯一的商户订单ID

    Args:
        prefix: 订单号前缀，默认为 "LINKPAY"

    Returns:
        JSON格式的生成结果，包含唯一的订单号
    """
    return get_linkpay_tool().generate_merchant_order_id(prefix)


@mcp.tool()
def create_linkpay_order(
        merchant_order_id: str,
        currency: str,
        amount: str,
        merchant_order_time: Optional[str] = None,
        goods_name: Optional[str] = None,
        goods_description: Optional[str] = None,
        trade_type: Optional[str] = None,
        return_url: Optional[str] = None,
        webhook_url: Optional[str] = None,
        enabled_payment_methods: Optional[List[str]] = None,
        valid_time: Optional[int] = None
) -> str:
    """创建 LinkPay 支付订单

    Args:
        merchant_order_id: 商户订单ID（必填）
        currency: 货币代码，如 "USD"（必填）
        amount: 支付金额（必填）
        merchant_order_time: 订单时间，默认当前时间
        goods_name: 商品名称
        goods_description: 商品描述
        trade_type: 交易类型
        return_url: 返回地址
        webhook_url: 回调地址
        enabled_payment_methods: 支持的支付方式列表
        valid_time: 有效时间（分钟）

    Returns:
        JSON格式的创建结果，包含支付链接
    """
    return get_linkpay_tool().create_linkpay_order(
        merchant_order_id=merchant_order_id,
        currency=currency,
        amount=amount,
        merchant_order_time=merchant_order_time,
        goods_name=goods_name,
        goods_description=goods_description,
        trade_type=trade_type,
        return_url=return_url,
        webhook_url=webhook_url,
        enabled_payment_methods=enabled_payment_methods,
        valid_time=valid_time
    )


@mcp.tool()
def query_linkpay_order(merchant_order_id: str) -> str:
    """查询 LinkPay 订单状态

    Args:
        merchant_order_id: 商户订单ID

    Returns:
        JSON格式的订单状态信息
    """
    return get_linkpay_tool().query_linkpay_order(merchant_order_id)


@mcp.tool()
def create_linkpay_refund(
        original_merchant_order_id: str,
        merchant_trans_id: str,
        currency: str,
        refund_amount: str,
        merchant_trans_time: Optional[str] = None,
        reason: Optional[str] = None,
        description: Optional[str] = None
) -> str:
    """创建 LinkPay 退款

    Args:
        original_merchant_order_id: 原始订单ID（必填）
        merchant_trans_id: 退款交易ID（必填）
        currency: 货币代码（必填）
        refund_amount: 退款金额（必填）
        merchant_trans_time: 退款时间，默认当前时间
        reason: 退款原因
        description: 退款描述

    Returns:
        JSON格式的退款结果
    """
    return get_linkpay_tool().create_linkpay_refund(
        original_merchant_order_id=original_merchant_order_id,
        merchant_trans_id=merchant_trans_id,
        currency=currency,
        refund_amount=refund_amount,
        merchant_trans_time=merchant_trans_time,
        reason=reason,
        description=description
    )


@mcp.tool()
def query_linkpay_refund(merchant_trans_id: str) -> str:
    """查询 LinkPay 退款状态

    Args:
        merchant_trans_id: 退款交易ID

    Returns:
        JSON格式的退款状态信息
    """
    return get_linkpay_tool().query_linkpay_refund(merchant_trans_id)


def main():
    required_env_vars = ['EVOCLOUD_BASE_URL', 'EVOCLOUD_SID', 'EVOCLOUD_SIGN_KEY']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print(f"错误：缺少必需的环境变量: {', '.join(missing_vars)}")
        sys.exit(1)

    # 获取参数 取不同的transport
    transport = sys.argv[1] if len(sys.argv) > 1 else 'sse'
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
