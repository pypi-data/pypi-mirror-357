"""
LinkPay Webhook 处理模块

本模块提供 LinkPay Webhook 通知的处理功能，包括：
- 支付状态通知处理
- 退款状态通知处理
- Webhook 签名验证
- 事件类型处理
"""

import hashlib
import hmac
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable, Union
from urllib.parse import parse_qs

from ..common import SignType, ValidationException
from .model import (
    Result, TransAmount, MerchantOrderInfo, OrderStatus, 
    RefundStatus, PaymentMethod, TransactionInfo
)

logger = logging.getLogger(__name__)


# ============================================================================
# Webhook Event Types
# ============================================================================

class WebhookEventType:
    """Webhook 事件类型常量"""
    PAYMENT_SUCCESS = "payment.success"
    PAYMENT_FAILED = "payment.failed"
    PAYMENT_PENDING = "payment.pending"
    PAYMENT_CANCELLED = "payment.cancelled"
    
    REFUND_SUCCESS = "refund.success"
    REFUND_FAILED = "refund.failed"
    REFUND_PENDING = "refund.pending"
    REFUND_CANCELLED = "refund.cancelled"


# ============================================================================
# Webhook Data Models
# ============================================================================

class PaymentWebhookData:
    """支付 Webhook 通知数据"""
    
    def __init__(self, data: Dict[str, Any]):
        self.event_type = data.get("eventType")
        self.event_id = data.get("eventId")
        self.event_time = data.get("eventTime")
        
        # 订单信息
        order_info = data.get("merchantOrderInfo", {})
        self.merchant_order_id = order_info.get("merchantOrderID")
        self.order_status = OrderStatus(order_info["status"]) if "status" in order_info else None
        
        # 交易金额
        amount_info = data.get("transAmount", {})
        self.trans_amount = TransAmount(
            currency=amount_info["currency"],
            value=amount_info["value"]
        ) if amount_info else None
        
        # 支付方式信息
        self.payment_method = data.get("paymentMethod")
        
        # 交易信息
        self.transaction_info = data.get("transactionInfo")
        
        # 其他信息
        self.metadata = data.get("metadata", {})
        self.raw_data = data
    
    def is_payment_success(self) -> bool:
        """判断是否为支付成功通知"""
        return self.event_type == WebhookEventType.PAYMENT_SUCCESS
    
    def is_payment_failed(self) -> bool:
        """判断是否为支付失败通知"""
        return self.event_type == WebhookEventType.PAYMENT_FAILED
    
    def __str__(self) -> str:
        return f"PaymentWebhook(event={self.event_type}, order={self.merchant_order_id}, status={self.order_status})"


class RefundWebhookData:
    """退款 Webhook 通知数据"""
    
    def __init__(self, data: Dict[str, Any]):
        self.event_type = data.get("eventType")
        self.event_id = data.get("eventId")
        self.event_time = data.get("eventTime")
        
        # 退款信息
        self.refund_id = data.get("refundId")
        self.merchant_trans_id = data.get("merchantTransId")
        self.original_merchant_order_id = data.get("originalMerchantOrderId")
        
        # 退款金额
        amount_info = data.get("refundAmount", {})
        self.refund_amount = TransAmount(
            currency=amount_info["currency"],
            value=amount_info["value"]
        ) if amount_info else None
        
        # 退款状态
        self.refund_status = RefundStatus(data["status"]) if "status" in data else None
        
        # 失败原因
        self.failure_reason = data.get("failureReason")
        
        # 其他信息
        self.metadata = data.get("metadata", {})
        self.raw_data = data
    
    def is_refund_success(self) -> bool:
        """判断是否为退款成功通知"""
        return self.event_type == WebhookEventType.REFUND_SUCCESS
    
    def is_refund_failed(self) -> bool:
        """判断是否为退款失败通知"""
        return self.event_type == WebhookEventType.REFUND_FAILED
    
    def __str__(self) -> str:
        return f"RefundWebhook(event={self.event_type}, refund={self.merchant_trans_id}, status={self.refund_status})"


# ============================================================================
# Webhook Handler Class
# ============================================================================

class LinkPayWebhookHandler:
    """LinkPay Webhook 处理器"""
    
    def __init__(self, sign_key: str, sign_type: SignType = SignType.SHA256):
        """
        初始化 Webhook 处理器
        
        Args:
            sign_key: 签名密钥
            sign_type: 签名算法类型
        """
        self.sign_key = sign_key
        self.sign_type = sign_type
        self._payment_handlers: Dict[str, Callable] = {}
        self._refund_handlers: Dict[str, Callable] = {}
    
    def register_payment_handler(self, event_type: str, handler: Callable[[PaymentWebhookData], None]):
        """
        注册支付事件处理器
        
        Args:
            event_type: 事件类型
            handler: 处理函数
        """
        self._payment_handlers[event_type] = handler
        logger.info(f"Registered payment handler for event type: {event_type}")
    
    def register_refund_handler(self, event_type: str, handler: Callable[[RefundWebhookData], None]):
        """
        注册退款事件处理器
        
        Args:
            event_type: 事件类型
            handler: 处理函数
        """
        self._refund_handlers[event_type] = handler
        logger.info(f"Registered refund handler for event type: {event_type}")
    
    def verify_signature(self, payload: str, signature: str, timestamp: str = None) -> bool:
        """
        验证 Webhook 签名
        
        Args:
            payload: 请求体内容
            signature: 签名值
            timestamp: 时间戳（可选）
            
        Returns:
            bool: 签名是否有效
        """
        try:
            # 构建签名字符串
            if timestamp:
                sign_string = f"{timestamp}.{payload}"
            else:
                sign_string = payload
            
            # 计算签名
            if self.sign_type == SignType.SHA256:
                expected_signature = hmac.new(
                    self.sign_key.encode('utf-8'),
                    sign_string.encode('utf-8'),
                    hashlib.sha256
                ).hexdigest()
            elif self.sign_type == SignType.MD5:
                expected_signature = hmac.new(
                    self.sign_key.encode('utf-8'),
                    sign_string.encode('utf-8'),
                    hashlib.md5
                ).hexdigest()
            else:
                raise ValidationException(f"Unsupported signature type: {self.sign_type}")
            
            # 比较签名
            is_valid = hmac.compare_digest(signature.lower(), expected_signature.lower())
            
            if is_valid:
                logger.debug("Webhook signature verification successful")
            else:
                logger.warning("Webhook signature verification failed")
                logger.debug(f"Expected: {expected_signature}, Got: {signature}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {e}")
            return False
    
    def handle_webhook(self, 
                      payload: str, 
                      signature: str, 
                      timestamp: str = None,
                      verify_signature: bool = True) -> Dict[str, Any]:
        """
        处理 Webhook 通知
        
        Args:
            payload: 请求体内容
            signature: 签名值
            timestamp: 时间戳
            verify_signature: 是否验证签名
            
        Returns:
            Dict[str, Any]: 处理结果
            
        Raises:
            ValidationException: 签名验证失败或数据格式错误
        """
        logger.info("Processing webhook notification")
        
        # 验证签名
        if verify_signature and not self.verify_signature(payload, signature, timestamp):
            raise ValidationException("Invalid webhook signature")
        
        try:
            # 解析 JSON 数据
            data = json.loads(payload)
            event_type = data.get("eventType")
            
            if not event_type:
                raise ValidationException("Missing eventType in webhook data")
            
            logger.info(f"Processing webhook event: {event_type}")
            
            # 根据事件类型处理
            if event_type.startswith("payment."):
                return self._handle_payment_webhook(data)
            elif event_type.startswith("refund."):
                return self._handle_refund_webhook(data)
            else:
                logger.warning(f"Unknown webhook event type: {event_type}")
                return {
                    "status": "ignored",
                    "message": f"Unknown event type: {event_type}"
                }
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in webhook payload: {e}")
            raise ValidationException("Invalid JSON format in webhook payload")
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            raise
    
    def _handle_payment_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理支付 Webhook"""
        webhook_data = PaymentWebhookData(data)
        event_type = webhook_data.event_type
        
        logger.info(f"Processing payment webhook: {webhook_data}")
        
        # 查找并执行处理器
        handler = self._payment_handlers.get(event_type)
        if handler:
            try:
                handler(webhook_data)
                logger.info(f"Payment webhook handled successfully: {event_type}")
                return {
                    "status": "success",
                    "message": f"Payment webhook processed: {event_type}",
                    "event_id": webhook_data.event_id
                }
            except Exception as e:
                logger.error(f"Error in payment webhook handler: {e}")
                return {
                    "status": "error",
                    "message": f"Handler error: {str(e)}",
                    "event_id": webhook_data.event_id
                }
        else:
            logger.warning(f"No handler registered for payment event: {event_type}")
            return {
                "status": "ignored",
                "message": f"No handler for event: {event_type}",
                "event_id": webhook_data.event_id
            }
    
    def _handle_refund_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理退款 Webhook"""
        webhook_data = RefundWebhookData(data)
        event_type = webhook_data.event_type
        
        logger.info(f"Processing refund webhook: {webhook_data}")
        
        # 查找并执行处理器
        handler = self._refund_handlers.get(event_type)
        if handler:
            try:
                handler(webhook_data)
                logger.info(f"Refund webhook handled successfully: {event_type}")
                return {
                    "status": "success",
                    "message": f"Refund webhook processed: {event_type}",
                    "event_id": webhook_data.event_id
                }
            except Exception as e:
                logger.error(f"Error in refund webhook handler: {e}")
                return {
                    "status": "error",
                    "message": f"Handler error: {str(e)}",
                    "event_id": webhook_data.event_id
                }
        else:
            logger.warning(f"No handler registered for refund event: {event_type}")
            return {
                "status": "ignored",
                "message": f"No handler for event: {event_type}",
                "event_id": webhook_data.event_id
            }


# ============================================================================
# Convenience Functions
# ============================================================================

def create_webhook_handler(sign_key: str, sign_type: SignType = SignType.SHA256) -> LinkPayWebhookHandler:
    """
    创建 Webhook 处理器的便捷函数
    
    Args:
        sign_key: 签名密钥
        sign_type: 签名算法类型
        
    Returns:
        LinkPayWebhookHandler: Webhook 处理器实例
    """
    return LinkPayWebhookHandler(sign_key, sign_type)


def parse_webhook_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """
    解析 Webhook 请求头
    
    Args:
        headers: HTTP 请求头字典
        
    Returns:
        Dict[str, str]: 解析后的 Webhook 相关头信息
    """
    webhook_headers = {}
    
    # 常见的 Webhook 头字段
    header_mappings = {
        'x-evo-signature': 'signature',
        'x-evo-timestamp': 'timestamp',
        'x-evo-event-type': 'event_type',
        'x-evo-event-id': 'event_id',
        'content-type': 'content_type'
    }
    
    for header_key, mapped_key in header_mappings.items():
        # 支持大小写不敏感的头字段查找
        for key, value in headers.items():
            if key.lower() == header_key.lower():
                webhook_headers[mapped_key] = value
                break
    
    return webhook_headers


def validate_webhook_timestamp(timestamp: str, tolerance_seconds: int = 300) -> bool:
    """
    验证 Webhook 时间戳是否在容忍范围内
    
    Args:
        timestamp: 时间戳字符串
        tolerance_seconds: 容忍的时间差（秒）
        
    Returns:
        bool: 时间戳是否有效
    """
    try:
        webhook_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        current_time = datetime.now(webhook_time.tzinfo)
        time_diff = abs((current_time - webhook_time).total_seconds())
        
        is_valid = time_diff <= tolerance_seconds
        
        if not is_valid:
            logger.warning(f"Webhook timestamp too old: {time_diff}s > {tolerance_seconds}s")
        
        return is_valid
        
    except Exception as e:
        logger.error(f"Error validating webhook timestamp: {e}")
        return False 