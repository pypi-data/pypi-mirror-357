"""
LinkPay API Client

This module provides the LinkPay client for interacting with EVO Cloud LinkPay APIs.
"""

import logging
from typing import Optional, Dict, Any
from urllib.parse import quote

from ..common import BaseClient, SignType, ValidationException, APIException
from .model import (
    LinkPayOrderRequest, LinkPayOrderResponse, LinkPayOrderQueryResponse,
    LinkPayRefundRequest, LinkPayRefundResponse, LinkPayRefundQueryResponse,
    validate_merchant_order_id, validate_currency_code, validate_amount_value,
    validate_merchant_trans_id, validate_refund_description
)

logger = logging.getLogger(__name__)


class LinkpayClient(BaseClient):
    """
    LinkPay API 客户端
    
    提供创建支付链接、查询订单状态等功能。
    """

    def __init__(self, base_url: str, sid: str, sign_key: str, sign_type: SignType = SignType.SHA256, timeout: int = 60, max_retries: int = 1):
        """
        初始化 LinkPay 客户端
        
        Args:
            base_url: EVO Cloud API 基础URL
            sid: 系统ID
            sign_key: 签名密钥
            sign_type: 签名算法类型
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        super().__init__(base_url, sign_key, sign_type, timeout, max_retries)
        self.sid = sid

    def create_linkpay_order(self, request: LinkPayOrderRequest) -> LinkPayOrderResponse:
        """
        创建 LinkPay 支付订单
        
        Args:
            request: LinkPay 订单请求对象
            
        Returns:
            LinkPayOrderResponse: 包含支付链接的响应对象
            
        Raises:
            ValidationException: 参数验证失败
            APIException: API 调用失败
            
        Example:
            ```python
            from datetime import datetime, timezone
            from linkpay.model import (
                LinkPayOrderRequest, MerchantOrderInfo, TransAmount, 
                TradeInfo, TradeType
            )
            
            # 创建订单请求
            order_info = MerchantOrderInfo(
                merchant_order_id="ORDER_20231201_001",
                merchant_order_time=datetime.now(timezone.utc).isoformat(),
                enabled_payment_method=["Alipay", "WeChat_Pay", "Visa"]
            )
            
            amount = TransAmount(currency="USD", value="100.50")
            
            trade_info = TradeInfo(
                trade_type=TradeType.SALE_OF_GOODS,
                goods_name="测试商品",
                goods_description="这是一个测试商品"
            )
            
            request = LinkPayOrderRequest(
                merchant_order_info=order_info,
                trans_amount=amount,
                trade_info=trade_info,
                return_url="https://merchant.com/return",
                webhook="https://merchant.com/webhook"
            )
            
            # 创建订单
            response = client.create_linkpay_order(request)
            
            if response.result.code == "S0000":
                print(f"支付链接: {response.link_url}")
                print(f"过期时间: {response.expiry_time}")
            else:
                print(f"创建失败: {response.result.message}")
            ```
        """
        # 参数验证
        self._validate_order_request(request)
        
        # 构建API路径
        url_path = f"/g2/v0/payment/mer/{self.sid}/evo.e-commerce.linkpay"
        
        # 转换请求数据
        request_data = request.to_dict()
        
        logger.info(f"Creating LinkPay order for merchant order ID: {request.merchant_order_info.merchant_order_id}")
        logger.debug(f"Request data: {request_data}")
        
        try:
            # 发送API请求
            response_data = self._make_request("POST", url_path, data=request_data)
            
            # 解析响应
            response = LinkPayOrderResponse.from_dict(response_data)
            
            if response.result.code == "S0000":
                logger.info(f"LinkPay order created successfully. Link URL: {response.link_url}")
            else:
                logger.warning(f"LinkPay order creation failed: {response.result.code} - {response.result.message}")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to create LinkPay order: {e}")
            raise

    def get_linkpay_order(self, merchant_order_id: str) -> LinkPayOrderQueryResponse:
        """
        查询 LinkPay 订单状态
        
        Args:
            merchant_order_id: 商户订单ID
            
        Returns:
            LinkPayOrderQueryResponse: 订单查询响应对象
            
        Raises:
            ValidationException: 参数验证失败
            APIException: API 调用失败
            
        Example:
            ```python
            # 查询订单状态
            response = client.get_linkpay_order("ORDER_20231201_001")
            
            if response.result.code == "S0000":
                order_info = response.merchant_order_info
                print(f"订单状态: {order_info.status}")
                print(f"订单ID: {order_info.merchant_order_id}")
                
                if response.transaction_info:
                    trans_info = response.transaction_info
                    print(f"交易金额: {trans_info.trans_amount.value} {trans_info.trans_amount.currency}")
                    print(f"交易状态: {trans_info.status}")
            else:
                print(f"查询失败: {response.result.message}")
            ```
        """
        # 参数验证
        if not merchant_order_id:
            raise ValidationException("Merchant order ID cannot be empty")
        
        if not validate_merchant_order_id(merchant_order_id):
            raise ValidationException("Invalid merchant order ID format")
        
        # 构建API路径，对订单ID进行URL编码
        encoded_order_id = quote(merchant_order_id, safe='')
        url_path = f"/g2/v0/payment/mer/{self.sid}/evo.e-commerce.linkpay/{encoded_order_id}"
        
        logger.info(f"Querying LinkPay order: {merchant_order_id}")
        
        try:
            # 发送API请求（GET请求不需要请求体）
            response_data = self._make_request("GET", url_path)
            
            # 解析响应
            response = LinkPayOrderQueryResponse.from_dict(response_data)
            
            if response.result.code == "S0000":
                logger.info(f"LinkPay order query successful for: {merchant_order_id}")
                if response.merchant_order_info:
                    logger.debug(f"Order status: {response.merchant_order_info.status}")
            else:
                logger.warning(f"LinkPay order query failed: {response.result.code} - {response.result.message}")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to query LinkPay order {merchant_order_id}: {e}")
            raise

    def _validate_order_request(self, request: LinkPayOrderRequest) -> None:
        """
        验证订单请求参数
        
        Args:
            request: 订单请求对象
            
        Raises:
            ValidationException: 验证失败时抛出异常
        """
        # 验证必填字段
        if not request.merchant_order_info:
            raise ValidationException("Merchant order info is required")
        
        if not request.trans_amount:
            raise ValidationException("Transaction amount is required")
        
        # 验证商户订单ID
        order_id = request.merchant_order_info.merchant_order_id
        if not validate_merchant_order_id(order_id):
            raise ValidationException(f"Invalid merchant order ID: {order_id}")
        
        # 验证订单时间格式
        order_time = request.merchant_order_info.merchant_order_time
        if not order_time:
            raise ValidationException("Merchant order time is required")
        
        # 验证货币代码
        currency = request.trans_amount.currency
        if not validate_currency_code(currency):
            raise ValidationException(f"Invalid currency code: {currency}")
        
        # 验证金额格式
        amount_value = request.trans_amount.value
        if not validate_amount_value(amount_value):
            raise ValidationException(f"Invalid amount value: {amount_value}")
        
        # 验证支付方式列表
        if request.merchant_order_info.enabled_payment_method:
            payment_methods = request.merchant_order_info.enabled_payment_method
            if len(payment_methods) > 2048:
                raise ValidationException("Too many payment methods specified")
        
        # 验证有效时间
        if request.valid_time is not None:
            if not (5 <= request.valid_time <= 43200):
                raise ValidationException("Valid time must be between 5 and 43200 minutes")
        
        # 验证URL格式
        if request.return_url and len(request.return_url) > 300:
            raise ValidationException("Return URL too long (max 300 characters)")
        
        if request.webhook and len(request.webhook) > 300:
            raise ValidationException("Webhook URL too long (max 300 characters)")
        
        # 验证用户信息
        if request.user_info:
            user_info = request.user_info
            if len(user_info.reference) > 64:
                raise ValidationException("User reference too long (max 64 characters)")
            if len(user_info.vault_id) > 36:
                raise ValidationException("Vault ID too long (max 36 characters)")
        
        # 验证商店信息
        if request.store_info and request.store_info.mcc:
            if len(request.store_info.mcc) != 4:
                raise ValidationException("MCC must be exactly 4 characters")
        
        logger.debug("Order request validation passed")

    def create_linkpay_refund(self, merchant_order_id: str, request: LinkPayRefundRequest) -> LinkPayRefundResponse:
        """
        创建 LinkPay 退款
        
        Args:
            merchant_order_id: 原始商户订单ID
            request: LinkPay 退款请求对象
            
        Returns:
            LinkPayRefundResponse: 退款响应对象
            
        Raises:
            ValidationException: 参数验证失败
            APIException: API 调用失败
            
        Example:
            ```python
            from datetime import datetime, timezone
            from linkpay.model import (
                LinkPayRefundRequest, TransAmount, RefundReason
            )
            
            # 创建退款请求
            refund_amount = TransAmount(currency="USD", value="50.00")
            
            request = LinkPayRefundRequest(
                merchant_trans_id="REFUND_20231201_001",
                merchant_trans_time=datetime.now(timezone.utc).isoformat(),
                refund_amount=refund_amount,
                reason=RefundReason.REQUESTED_BY_CUSTOMER,
                description="客户要求退款"
            )
            
            # 创建退款
            response = client.create_linkpay_refund("ORDER_20231201_001", request)
            
            if response.result.code == "S0000":
                print(f"退款ID: {response.refund_id}")
                print(f"退款状态: {response.status}")
            else:
                print(f"退款失败: {response.result.message}")
            ```
        """
        # 参数验证
        self._validate_refund_request(merchant_order_id, request)
        
        # 构建API路径，对订单ID进行URL编码
        encoded_order_id = quote(merchant_order_id, safe='')
        url_path = f"/g2/v0/payment/mer/{self.sid}/evo.e-commerce.linkpayRefund/{encoded_order_id}"
        
        # 转换请求数据
        request_data = request.to_dict()
        
        logger.info(f"Creating LinkPay refund for order: {merchant_order_id}, refund trans ID: {request.merchant_trans_id}")
        logger.debug(f"Refund request data: {request_data}")
        
        try:
            # 发送API请求
            response_data = self._make_request("POST", url_path, data=request_data)
            
            # 解析响应
            response = LinkPayRefundResponse.from_dict(response_data)
            
            if response.result.code == "S0000":
                logger.info(f"LinkPay refund created successfully. Refund ID: {response.refund_id}")
            else:
                logger.warning(f"LinkPay refund creation failed: {response.result.code} - {response.result.message}")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to create LinkPay refund for order {merchant_order_id}: {e}")
            raise

    def get_linkpay_refund(self, merchant_trans_id: str) -> LinkPayRefundQueryResponse:
        """
        查询 LinkPay 退款状态
        
        Args:
            merchant_trans_id: 商户退款交易ID
            
        Returns:
            LinkPayRefundQueryResponse: 退款查询响应对象
            
        Raises:
            ValidationException: 参数验证失败
            APIException: API 调用失败
            
        Example:
            ```python
            # 查询退款状态
            response = client.get_linkpay_refund("REFUND_20231201_001")
            
            if response.result.code == "S0000":
                print(f"退款ID: {response.refund_id}")
                print(f"退款状态: {response.status}")
                print(f"退款金额: {response.refund_amount.value} {response.refund_amount.currency}")
                print(f"原始订单ID: {response.original_merchant_order_id}")
                
                if response.failure_reason:
                    print(f"失败原因: {response.failure_reason}")
            else:
                print(f"查询失败: {response.result.message}")
            ```
        """
        # 参数验证
        if not merchant_trans_id:
            raise ValidationException("Merchant transaction ID cannot be empty")
        
        if not validate_merchant_trans_id(merchant_trans_id):
            raise ValidationException("Invalid merchant transaction ID format")
        
        # 构建API路径，对交易ID进行URL编码
        encoded_trans_id = quote(merchant_trans_id, safe='')
        url_path = f"/g2/v0/payment/mer/{self.sid}/evo.e-commerce.linkpayRefund/{encoded_trans_id}"
        
        logger.info(f"Querying LinkPay refund: {merchant_trans_id}")
        
        try:
            # 发送API请求（GET请求不需要请求体）
            response_data = self._make_request("GET", url_path)
            
            # 解析响应
            response = LinkPayRefundQueryResponse.from_dict(response_data)
            
            if response.result.code == "S0000":
                logger.info(f"LinkPay refund query successful for: {merchant_trans_id}")
                if response.status:
                    logger.debug(f"Refund status: {response.status}")
            else:
                logger.warning(f"LinkPay refund query failed: {response.result.code} - {response.result.message}")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to query LinkPay refund {merchant_trans_id}: {e}")
            raise

    def _validate_refund_request(self, merchant_order_id: str, request: LinkPayRefundRequest) -> None:
        """
        验证退款请求参数
        
        Args:
            merchant_order_id: 原始商户订单ID
            request: 退款请求对象
            
        Raises:
            ValidationException: 验证失败时抛出异常
        """
        # 验证原始订单ID
        if not validate_merchant_order_id(merchant_order_id):
            raise ValidationException(f"Invalid merchant order ID: {merchant_order_id}")
        
        # 验证必填字段
        if not request.merchant_trans_id:
            raise ValidationException("Merchant transaction ID is required")
        
        if not request.merchant_trans_time:
            raise ValidationException("Merchant transaction time is required")
        
        if not request.refund_amount:
            raise ValidationException("Refund amount is required")
        
        # 验证商户交易ID
        if not validate_merchant_trans_id(request.merchant_trans_id):
            raise ValidationException(f"Invalid merchant transaction ID: {request.merchant_trans_id}")
        
        # 验证货币代码
        currency = request.refund_amount.currency
        if not validate_currency_code(currency):
            raise ValidationException(f"Invalid currency code: {currency}")
        
        # 验证金额格式
        amount_value = request.refund_amount.value
        if not validate_amount_value(amount_value):
            raise ValidationException(f"Invalid refund amount value: {amount_value}")
        
        # 验证退款描述
        if request.description and not validate_refund_description(request.description):
            raise ValidationException("Refund description too long (max 255 characters)")
        
        # 验证元数据
        if request.metadata:
            if len(request.metadata) > 50:
                raise ValidationException("Too many metadata entries (max 50)")
            
            for key, value in request.metadata.items():
                if len(key) > 40:
                    raise ValidationException(f"Metadata key too long: {key} (max 40 characters)")
                if len(value) > 500:
                    raise ValidationException(f"Metadata value too long for key {key} (max 500 characters)")
        
        logger.debug("Refund request validation passed")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        # 清理资源（如果需要）
        pass

    