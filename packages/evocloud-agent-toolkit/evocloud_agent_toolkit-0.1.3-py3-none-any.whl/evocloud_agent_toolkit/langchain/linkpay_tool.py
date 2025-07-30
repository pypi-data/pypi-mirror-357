"""
EvoCloud LinkPay LangChain Tools

This module provides LangChain tools for EvoCloud LinkPay payment services.
"""

import json
import logging
from datetime import datetime, timezone
import os
from typing import Optional, List
from langchain_core.tools import StructuredTool
from evocloud_sdk.client import EVOCloudClient
from evocloud_sdk.linkpay.model import (
    LinkPayOrderRequest, LinkPayRefundRequest, MerchantOrderInfo,
    TransAmount, TradeInfo, TradeType, RefundReason,
    validate_merchant_order_id, validate_currency_code, validate_amount_value,
    validate_merchant_trans_id, validate_refund_description
)
from evocloud_sdk.common import ValidationException, APIException
from evocloud_sdk.common.utils import generate_order_id

logger = logging.getLogger(__name__)


class EvoCloudLinkPayTool:
    """EvoCloud LinkPay 工具类"""

    def __init__(self, base_url: Optional[str] = None, sid: Optional[str] = None, sign_key: Optional[str] = None,
                 webhook_url: Optional[str] = None, tools: Optional[List[str]] = None):
        """
        初始化 LinkPay 工具类
        
        Args:
            base_url: 请求地址
            sid: 商户号
            sign_key: 商户签名密钥
            webhook_url: 默认回调地址（可选）
        """
        self.client = EVOCloudClient(base_url=base_url, sid=sid, sign_key=sign_key)
        self.webhook_url = webhook_url if webhook_url else os.getenv("EVOCLOUD_WEBHOOK_URL")
        self._enabled_tools = tools if tools else ["generate_merchant_order_id", "create_linkpay_order",
                                                   "query_linkpay_order", "create_linkpay_refund",
                                                   "query_linkpay_refund"]
        self._tools = None

    def generate_merchant_order_id(self, prefix: str = "LINKPAY") -> str:
        """生成唯一的商户订单ID
        
        Args:
            prefix: 订单号前缀，默认为 "LINKPAY"
            
        Returns:
            JSON格式的生成结果，包含唯一的订单号
        """
        try:
            order_id = generate_order_id(prefix)

            result = {
                "success": True,
                "message": "Order ID generated successfully",
                "data": {
                    "merchant_order_id": order_id,
                    "prefix": prefix,
                    "generated_at": datetime.now(timezone.utc).isoformat()
                }
            }

            logger.info(f"Generated order ID: {order_id}")
            return json.dumps(result, ensure_ascii=False, indent=2)

        except Exception as e:
            error_result = {
                "success": False,
                "message": f"Error generating order ID: {str(e)}",
                "data": {
                    "prefix": prefix,
                    "error": str(e)
                }
            }
            logger.error(f"Failed to generate order ID with prefix {prefix}: {e}")
            return json.dumps(error_result, ensure_ascii=False, indent=2)

    def create_linkpay_order(
            self,
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
            webhook_url: 回调地址，默认使用类初始化时的地址
            enabled_payment_methods: 支持的支付方式列表
            valid_time: 有效时间（分钟）
            
        Returns:
            JSON格式的创建结果，包含支付链接
        """
        try:
            # 参数验证
            full_merchant_order_id = merchant_order_id

            if len(merchant_order_id) > 32:  # 临时处理
                merchant_order_id = merchant_order_id[:32]
            if not validate_merchant_order_id(merchant_order_id):
                raise ValidationException(f"Invalid merchant_order_id: {merchant_order_id}")

            if not validate_currency_code(currency):
                raise ValidationException(f"Invalid currency: {currency}")

            if not validate_amount_value(amount):
                raise ValidationException(f"Invalid amount: {amount}")
            return_url = return_url or f"https://example.com?id={full_merchant_order_id}"
            # 生成默认时间戳
            if not merchant_order_time:
                merchant_order_time = datetime.now(timezone.utc).isoformat()

            # 使用默认 webhook_url
            final_webhook_url = webhook_url or self.webhook_url

            # 构建订单信息
            merchant_order_info = MerchantOrderInfo(
                merchant_order_id=merchant_order_id,
                merchant_order_time=merchant_order_time,
                enabled_payment_method=enabled_payment_methods
            )

            trans_amount = TransAmount(currency=currency, value=amount)

            # 构建交易信息
            trade_info = None
            if goods_name or goods_description or trade_type:
                trade_info = TradeInfo(
                    goods_name=goods_name,
                    goods_description=goods_description,
                    trade_type=TradeType(trade_type) if trade_type else TradeType.OTHERS
                )

            # 创建请求对象
            request = LinkPayOrderRequest(
                merchant_order_info=merchant_order_info,
                trans_amount=trans_amount,
                trade_info=trade_info,
                return_url=return_url,
                webhook=final_webhook_url,
                valid_time=valid_time
            )

            # 调用 SDK
            response = self.client.linkpay.create_linkpay_order(request)

            # 格式化返回结果
            result = {
                "success": True,
                "message": "Payment order created successfully",
                "data": {
                    "merchant_order_id": merchant_order_id,
                    "link_url": response.link_url,
                    "expiry_time": response.expiry_time,
                    "result_code": response.result.code,
                    "result_message": response.result.message
                }
            }

            if response.result.code == "S0000":
                logger.info(f"LinkPay order created successfully: {merchant_order_id}")
            else:
                result["success"] = False
                result["message"] = f"Failed to create payment order: {response.result.message}"
                logger.warning(f"LinkPay order creation failed: {response.result.code} - {response.result.message}")
                logger.info(f"LinkPay order creation failed: {json.dumps(response, ensure_ascii=False, indent=2)}")

            return json.dumps(result, ensure_ascii=False, indent=2)

        except (ValidationException, APIException) as e:
            error_result = {
                "success": False,
                "message": f"Error creating payment order: {str(e)}",
                "data": {
                    "merchant_order_id": merchant_order_id,
                    "error": str(e)
                }
            }
            logger.error(f"Failed to create LinkPay order {merchant_order_id}: {e}")
            return json.dumps(error_result, ensure_ascii=False, indent=2)

    def query_linkpay_order(self, merchant_order_id: str) -> str:
        """查询 LinkPay 订单状态
        
        Args:
            merchant_order_id: 商户订单ID
            
        Returns:
            JSON格式的订单状态信息
        """
        try:
            # 参数验证
            if not validate_merchant_order_id(merchant_order_id):
                raise ValidationException(f"Invalid merchant_order_id: {merchant_order_id}")

            # 调用 SDK
            response = self.client.linkpay.get_linkpay_order(merchant_order_id)

            # 格式化返回结果
            result = {
                "success": True,
                "message": "Order query successful",
                "data": {
                    "merchant_order_id": merchant_order_id,
                    "result_code": response.result.code,
                    "result_message": response.result.message
                }
            }

            if response.result.code == "S0000" and response.merchant_order_info:
                order_info = response.merchant_order_info
                result["data"].update({
                    "order_status": order_info.status.value if order_info.status else None,
                    "related_transactions": order_info.related_transactions
                })

                if response.transaction_info:
                    trans_info = response.transaction_info
                    result["data"]["transaction_info"] = {
                        "transaction_amount": {
                            "currency": trans_info.trans_amount.currency,
                            "value": trans_info.trans_amount.value
                        } if trans_info.trans_amount else None,
                        "status": trans_info.status
                    }

                logger.info(f"LinkPay order query successful: {merchant_order_id}")
            else:
                result["success"] = False
                result["message"] = f"Failed to query order: {response.result.message}"
                logger.warning(f"LinkPay order query failed: {response.result.code} - {response.result.message}")

            return json.dumps(result, ensure_ascii=False, indent=2)

        except (ValidationException, APIException) as e:
            error_result = {
                "success": False,
                "message": f"Error querying order: {str(e)}",
                "data": {
                    "merchant_order_id": merchant_order_id,
                    "error": str(e)
                }
            }
            logger.error(f"Failed to query LinkPay order {merchant_order_id}: {e}")
            return json.dumps(error_result, ensure_ascii=False, indent=2)

    def create_linkpay_refund(
            self,
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
        try:
            # 参数验证
            if not validate_merchant_order_id(original_merchant_order_id):
                raise ValidationException(f"Invalid original_merchant_order_id: {original_merchant_order_id}")

            if not validate_merchant_trans_id(merchant_trans_id):
                raise ValidationException(f"Invalid merchant_trans_id: {merchant_trans_id}")

            if not validate_currency_code(currency):
                raise ValidationException(f"Invalid currency: {currency}")

            if not validate_amount_value(refund_amount):
                raise ValidationException(f"Invalid refund_amount: {refund_amount}")

            if description and not validate_refund_description(description):
                raise ValidationException("Refund description too long (max 255 characters)")

            # 生成默认时间戳
            if not merchant_trans_time:
                merchant_trans_time = datetime.now(timezone.utc).isoformat()

            # 构建退款请求
            trans_amount = TransAmount(currency=currency, value=refund_amount)

            request = LinkPayRefundRequest(
                merchant_trans_id=merchant_trans_id,
                merchant_trans_time=merchant_trans_time,
                refund_amount=trans_amount,
                reason=RefundReason(reason) if reason else None,
                description=description
            )

            # 调用 SDK
            response = self.client.linkpay.create_linkpay_refund(original_merchant_order_id, request)

            # 格式化返回结果
            result = {
                "success": True,
                "message": "Refund created successfully",
                "data": {
                    "original_merchant_order_id": original_merchant_order_id,
                    "merchant_trans_id": merchant_trans_id,
                    "result_code": response.result.code,
                    "result_message": response.result.message
                }
            }

            if response.result.code == "S0000":
                result["data"].update({
                    "refund_id": response.refund_id,
                    "refund_amount": {
                        "currency": response.refund_amount.currency,
                        "value": response.refund_amount.value
                    } if response.refund_amount else None,
                    "status": response.status.value if response.status else None,
                    "created_time": response.created_time
                })
                logger.info(f"LinkPay refund created successfully: {merchant_trans_id}")
            else:
                result["success"] = False
                result["message"] = f"Failed to create refund: {response.result.message}"
                logger.warning(f"LinkPay refund creation failed: {response.result.code} - {response.result.message}")

            return json.dumps(result, ensure_ascii=False, indent=2)

        except (ValidationException, APIException) as e:
            error_result = {
                "success": False,
                "message": f"Error creating refund: {str(e)}",
                "data": {
                    "original_merchant_order_id": original_merchant_order_id,
                    "merchant_trans_id": merchant_trans_id,
                    "error": str(e)
                }
            }
            logger.error(f"Failed to create LinkPay refund {merchant_trans_id}: {e}")
            return json.dumps(error_result, ensure_ascii=False, indent=2)

    def query_linkpay_refund(self, merchant_trans_id: str) -> str:
        """查询 LinkPay 退款状态
        
        Args:
            merchant_trans_id: 退款交易ID
            
        Returns:
            JSON格式的退款状态信息
        """
        try:
            # 参数验证
            if not validate_merchant_trans_id(merchant_trans_id):
                raise ValidationException(f"Invalid merchant_trans_id: {merchant_trans_id}")

            # 调用 SDK
            response = self.client.linkpay.get_linkpay_refund(merchant_trans_id)

            # 格式化返回结果
            result = {
                "success": True,
                "message": "Refund query successful",
                "data": {
                    "merchant_trans_id": merchant_trans_id,
                    "result_code": response.result.code,
                    "result_message": response.result.message
                }
            }

            if response.result.code == "S0000":
                result["data"].update({
                    "refund_id": response.refund_id,
                    "original_merchant_order_id": response.original_merchant_order_id,
                    "refund_amount": {
                        "currency": response.refund_amount.currency,
                        "value": response.refund_amount.value
                    } if response.refund_amount else None,
                    "status": response.refund_status.value if response.refund_status else None,
                    "reason": response.reason.value if response.reason else None,
                    "description": response.description,
                    "created_time": response.created_time,
                    "updated_time": response.updated_time,
                    "failure_reason": response.failure_reason
                })
                logger.info(f"LinkPay refund query successful: {merchant_trans_id}")
            else:
                result["success"] = False
                result["message"] = f"Failed to query refund: {response.result.message}"
                logger.warning(f"LinkPay refund query failed: {response.result.code} - {response.result.message}")

            return json.dumps(result, ensure_ascii=False, indent=2)

        except (ValidationException, APIException) as e:
            error_result = {
                "success": False,
                "message": f"Error querying refund: {str(e)}",
                "data": {
                    "merchant_trans_id": merchant_trans_id,
                    "error": str(e)
                }
            }
            logger.error(f"Failed to query LinkPay refund {merchant_trans_id}: {e}")
            return json.dumps(error_result, ensure_ascii=False, indent=2)

    def get_tools(self) -> List[StructuredTool]:
        """获取所有 LinkPay 工具"""
        if self._tools is None:
            self._tools = [
                StructuredTool.from_function(
                    func=self.generate_merchant_order_id,
                    name="generate_merchant_order_id",
                    description="生成唯一的商户订单ID。可以指定前缀，默认为 'LINKPAY'。"
                ),
                StructuredTool.from_function(
                    func=self.create_linkpay_order,
                    name="create_linkpay_order",
                    description="创建 LinkPay 支付订单，生成支付链接。需要提供订单ID、货币代码和金额。"
                ),
                StructuredTool.from_function(
                    func=self.query_linkpay_order,
                    name="query_linkpay_order",
                    description="查询 LinkPay 订单状态和详细信息。需要提供订单ID。"
                ),
                StructuredTool.from_function(
                    func=self.create_linkpay_refund,
                    name="create_linkpay_refund",
                    description="创建 LinkPay 退款申请。需要提供原始订单ID、退款交易ID、货币代码和退款金额。"
                ),
                StructuredTool.from_function(
                    func=self.query_linkpay_refund,
                    name="query_linkpay_refund",
                    description="查询 LinkPay 退款状态和详细信息。需要提供退款交易ID。"
                )
            ]
        return self._tools
