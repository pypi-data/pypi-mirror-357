"""
LinkPay API Data Models

This module contains all data models for LinkPay API operations,
including request/response models, enums, and utility classes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Union
import json


# ============================================================================
# Enums and Constants
# ============================================================================

class OrderType(str, Enum):
    """订单类型枚举"""
    SINGLE = "Single"
    MULTIPLE = "Multiple"


class OrderStatus(str, Enum):
    """订单状态枚举"""
    PENDING = "Pending"
    ACTIVE = "Active"
    PAID = "Paid"
    CLOSED = "Closed"
    REFUNDED = "Refunded"
    PARTIAL_REFUNDED = "Partial Refunded"
    REFUNDING = "Refunding"
    FAILED = "Failed"


class TradeType(str, Enum):
    """交易类型枚举"""
    HOTEL = "Hotel"
    AIRLINE = "Airline"
    SALE_OF_GOODS = "Sale of goods"
    FUNDING_TRANSFER = "Funding_Transfer"
    WALLET_TRANSFER = "Wallet_Transfer"
    OTHERS = "Others"


class PaymentMethodType(str, Enum):
    """支付方式类型枚举"""
    CARD = "card"
    E_WALLET = "e-wallet"
    POINTS = "points"
    ONLINE_BANKING = "onlineBanking"
    BANK_TRANSFER = "bankTransfer"
    BUY_NOW_PAY_LATER = "buyNowPayLater"
    CARRIER_BILLING = "carrierBilling"
    CASH = "cash"
    PREPAID_CARD = "prepaidCard"


class FundingType(str, Enum):
    """资金类型枚举"""
    CREDIT = "credit"
    DEBIT = "debit"
    PREPAID = "prepaid"


class AccountType(str, Enum):
    """账户类型枚举"""
    RTN = "RTN"
    IBAN = "IBAN"
    CARD_ACCOUNT = "Card_Account"
    EMAIL = "Email"
    PHONE_NUMBER = "Phone_Number"
    BAN_BIC = "BAN_BIC"
    WALLET_ID = "Wallet_ID"
    SOCIAL_NETWORK_ID = "Social_network_ID"
    OTHER = "Other"


# ============================================================================
# Basic Data Types
# ============================================================================

@dataclass
class TransAmount:
    """交易金额"""
    currency: str  # ISO-4217 三位货币代码，如 "USD"
    value: str     # 金额字符串，如 "123.45"
    
    def __post_init__(self):
        if len(self.currency) != 3:
            raise ValueError("Currency must be 3-character ISO-4217 code")
        if not self.value:
            raise ValueError("Value cannot be empty")


@dataclass
class Address:
    """地址信息"""
    city: Optional[str] = None
    country: Optional[str] = None  # ISO-3166-1 alpha-3，如 "CHN"
    state_or_province: Optional[str] = None  # ISO 3166-2
    street: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    address_line3: Optional[str] = None
    house_number_or_name: Optional[str] = None
    postal_code: Optional[str] = None


@dataclass
class Name:
    """姓名信息"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None


@dataclass
class MobilePhone:
    """手机号码"""
    country_code: Optional[str] = None  # 国家代码，如 "+86"
    subscriber_sections: Optional[str] = None  # 号码部分
    area_code: Optional[str] = None  # 区号，如 "+852"
    phone_number: Optional[str] = None  # 电话号码


@dataclass
class Result:
    """API 结果"""
    code: str     # 结果代码，"S0000" 表示成功
    message: str  # 结果消息


# ============================================================================
# Merchant Order Info
# ============================================================================

@dataclass
class MerchantOrderInfo:
    """商户订单信息"""
    merchant_order_id: str  # 商户订单ID，最大32位
    merchant_order_time: str  # 订单创建时间，RFC3339格式
    order_type: Optional[OrderType] = OrderType.SINGLE
    enabled_payment_method: Optional[List[str]] = None
    is_collect_billing_address: Optional[bool] = False
    is_collect_email: Optional[bool] = False
    is_collect_full_name: Optional[bool] = False
    is_collect_phone_number: Optional[bool] = False
    is_collect_shipping_address: Optional[bool] = False
    status: Optional[OrderStatus] = None
    related_transactions: Optional[List[str]] = None


# ============================================================================
# Trade Info
# ============================================================================

@dataclass
class TradeInfo:
    """交易信息"""
    trade_type: Optional[TradeType] = None
    goods_name: Optional[str] = None
    goods_description: Optional[str] = None
    total_quantity: Optional[int] = None
    hotel_name: Optional[str] = None
    check_in_time: Optional[str] = None  # RFC3339格式
    check_out_time: Optional[str] = None  # RFC3339格式
    flight_number: Optional[str] = None
    departure_time: Optional[str] = None  # RFC3339格式
    purpose_of_payment: Optional[str] = None


# ============================================================================
# User Info
# ============================================================================

@dataclass
class UserInfo:
    """用户信息"""
    reference: str  # 用户引用ID，最大64位
    vault_id: str   # Vault ID，最大36位
    name: Optional[Name] = None
    mobile_phone: Optional[MobilePhone] = None
    billing_address: Optional[Address] = None
    delivery_address: Optional[Address] = None


# ============================================================================
# Store Info
# ============================================================================

@dataclass
class StoreInfo:
    """商店信息"""
    mcc: Optional[str] = None  # 商户类别代码，4位


# ============================================================================
# Sender/Recipient Info (for funding transfer)
# ============================================================================

@dataclass
class SenderInfo:
    """发送方信息（用于资金转账）"""
    name: Optional[Name] = None
    address: Optional[Address] = None


@dataclass
class RecipientInfo:
    """接收方信息（用于资金转账）"""
    account_number: Optional[str] = None
    account_type: Optional[AccountType] = None
    name: Optional[Name] = None
    address: Optional[Address] = None


# ============================================================================
# Payment Method Info
# ============================================================================

@dataclass
class CardInfo:
    """银行卡信息"""
    first6_no: str  # 卡号前6位
    last4_no: str   # 卡号后4位
    payment_brand: Optional[str] = None
    holder_name: Optional[str] = None
    funding_type: Optional[FundingType] = None
    issuing_bank: Optional[str] = None
    issuing_country: Optional[str] = None
    issuer_country: Optional[str] = None
    is_commercial: Optional[bool] = None


@dataclass
class EWalletInfo:
    """电子钱包信息"""
    payment_brand: Optional[str] = None
    consumer_account: Optional[str] = None
    consumer_id: Optional[str] = None


@dataclass
class OnlineBankingInfo:
    """网银信息"""
    payment_brand: str


@dataclass
class BankTransferInfo:
    """银行转账信息"""
    payment_brand: Optional[str] = None
    account_number: Optional[str] = None


@dataclass
class BuyNowPayLaterInfo:
    """先买后付信息"""
    payment_brand: Optional[str] = None


@dataclass
class CarrierBillingInfo:
    """运营商计费信息"""
    payment_brand: Optional[str] = None


@dataclass
class CashInfo:
    """现金支付信息"""
    payment_brand: Optional[str] = None


@dataclass
class PointsInfo:
    """积分支付信息"""
    payment_brand: str


@dataclass
class PrepaidCardInfo:
    """预付卡信息"""
    payment_brand: Optional[str] = None


@dataclass
class PaymentMethod:
    """支付方式"""
    type: PaymentMethodType
    payment_method_variant: Optional[str] = None
    card_info: Optional[CardInfo] = None
    e_wallet_info: Optional[EWalletInfo] = None
    online_banking_info: Optional[OnlineBankingInfo] = None
    bank_transfer_info: Optional[BankTransferInfo] = None
    buy_now_pay_later_info: Optional[BuyNowPayLaterInfo] = None
    carrier_billing_info: Optional[CarrierBillingInfo] = None
    cash_info: Optional[CashInfo] = None
    points_info: Optional[PointsInfo] = None
    prepaid_card_info: Optional[PrepaidCardInfo] = None


# ============================================================================
# Transaction Info
# ============================================================================

@dataclass
class MerchantTransInfo:
    """商户交易信息"""
    merchant_trans_id: str
    merchant_trans_time: str  # RFC3339格式
    merchant_order_reference: Optional[str] = None


@dataclass
class EvoTransInfo:
    """EVO Cloud 交易信息"""
    evo_trans_id: str
    evo_trans_time: str  # RFC3339格式
    retrieval_reference_num: Optional[str] = None
    trace_num: Optional[str] = None


@dataclass
class PspTransInfo:
    """PSP 交易信息"""
    psp_trans_id: Optional[str] = None
    authorization_code: Optional[str] = None


@dataclass
class FXRate:
    """汇率信息"""
    value: str
    base_currency: str
    quote_currency: str
    date: Optional[str] = None
    source: Optional[str] = None


@dataclass
class TransactionInfo:
    """交易信息"""
    merchant_trans_info: MerchantTransInfo
    trans_amount: TransAmount
    status: Optional[str] = None
    evo_trans_info: Optional[EvoTransInfo] = None
    psp_trans_info: Optional[PspTransInfo] = None
    billing_amount: Optional[TransAmount] = None
    billing_fx_rate: Optional[FXRate] = None
    convert_trans_amount: Optional[TransAmount] = None
    convert_trans_fx_rate: Optional[FXRate] = None


# ============================================================================
# LinkPay Order Request/Response Models
# ============================================================================

@dataclass
class LinkPayOrderRequest:
    """创建 LinkPay 订单请求"""
    merchant_order_info: MerchantOrderInfo
    trans_amount: TransAmount
    trade_info: Optional[TradeInfo] = None
    user_info: Optional[UserInfo] = None
    store_info: Optional[StoreInfo] = None
    sender_info: Optional[SenderInfo] = None
    recipient_info: Optional[RecipientInfo] = None
    return_url: Optional[str] = None
    webhook: Optional[str] = None
    valid_time: Optional[int] = None  # 5-43200分钟
    # 已弃用字段
    delivery_address: Optional[Address] = None
    payer_info: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于API请求"""
        result = {}
        
        # 处理必填字段
        result["merchantOrderInfo"] = {
            "merchantOrderID": self.merchant_order_info.merchant_order_id,
            "merchantOrderTime": self.merchant_order_info.merchant_order_time,
        }
        
        if self.merchant_order_info.order_type:
            result["merchantOrderInfo"]["orderType"] = self.merchant_order_info.order_type.value
            
        if self.merchant_order_info.enabled_payment_method:
            result["merchantOrderInfo"]["enabledPaymentMethod"] = self.merchant_order_info.enabled_payment_method
            
        # 添加收集信息标志
        if self.merchant_order_info.is_collect_billing_address is not None:
            result["merchantOrderInfo"]["isCollectBillingAddress"] = self.merchant_order_info.is_collect_billing_address
        if self.merchant_order_info.is_collect_email is not None:
            result["merchantOrderInfo"]["isCollectEmail"] = self.merchant_order_info.is_collect_email
        if self.merchant_order_info.is_collect_full_name is not None:
            result["merchantOrderInfo"]["isCollectFullName"] = self.merchant_order_info.is_collect_full_name
        if self.merchant_order_info.is_collect_phone_number is not None:
            result["merchantOrderInfo"]["isCollectPhoneNumber"] = self.merchant_order_info.is_collect_phone_number
        if self.merchant_order_info.is_collect_shipping_address is not None:
            result["merchantOrderInfo"]["isCollectShippingAddress"] = self.merchant_order_info.is_collect_shipping_address
        
        result["transAmount"] = {
            "currency": self.trans_amount.currency,
            "value": self.trans_amount.value
        }
        
        # 处理可选字段
        if self.trade_info:
            trade_dict = {}
            if self.trade_info.trade_type:
                trade_dict["tradeType"] = self.trade_info.trade_type.value
            if self.trade_info.goods_name:
                trade_dict["goodsName"] = self.trade_info.goods_name
            if self.trade_info.goods_description:
                trade_dict["goodsDescription"] = self.trade_info.goods_description
            if self.trade_info.total_quantity is not None:
                trade_dict["totalQuantity"] = self.trade_info.total_quantity
            if self.trade_info.hotel_name:
                trade_dict["hotelName"] = self.trade_info.hotel_name
            if self.trade_info.check_in_time:
                trade_dict["checkInTime"] = self.trade_info.check_in_time
            if self.trade_info.check_out_time:
                trade_dict["checkOutTime"] = self.trade_info.check_out_time
            if self.trade_info.flight_number:
                trade_dict["flightNumber"] = self.trade_info.flight_number
            if self.trade_info.departure_time:
                trade_dict["departureTime"] = self.trade_info.departure_time
            if self.trade_info.purpose_of_payment:
                trade_dict["purposeOfPayment"] = self.trade_info.purpose_of_payment
            
            if trade_dict:
                result["tradeInfo"] = trade_dict
        
        if self.user_info:
            user_dict = {
                "reference": self.user_info.reference,
                "vaultID": self.user_info.vault_id
            }
            
            if self.user_info.name:
                name_dict = {}
                if self.user_info.name.given_name:
                    name_dict["givenName"] = self.user_info.name.given_name
                if self.user_info.name.family_name:
                    name_dict["familyName"] = self.user_info.name.family_name
                if name_dict:
                    user_dict["name"] = name_dict
            
            if self.user_info.mobile_phone:
                phone_dict = {}
                if self.user_info.mobile_phone.country_code:
                    phone_dict["countryCode"] = self.user_info.mobile_phone.country_code
                if self.user_info.mobile_phone.subscriber_sections:
                    phone_dict["subscriberSections"] = self.user_info.mobile_phone.subscriber_sections
                if phone_dict:
                    user_dict["mobilePhone"] = phone_dict
            
            # 处理地址信息
            if self.user_info.billing_address:
                addr = self.user_info.billing_address
                addr_dict = {}
                if addr.city:
                    addr_dict["city"] = addr.city
                if addr.country:
                    addr_dict["country"] = addr.country
                if addr.postal_code:
                    addr_dict["postalCode"] = addr.postal_code
                if addr.state_or_province:
                    addr_dict["stateOrProvince"] = addr.state_or_province
                if addr.address_line1:
                    addr_dict["addressLine1"] = addr.address_line1
                if addr.address_line2:
                    addr_dict["addressLine2"] = addr.address_line2
                if addr.address_line3:
                    addr_dict["addressLine3"] = addr.address_line3
                if addr_dict:
                    user_dict["billingAddress"] = addr_dict
            
            if self.user_info.delivery_address:
                addr = self.user_info.delivery_address
                addr_dict = {}
                if addr.city:
                    addr_dict["city"] = addr.city
                if addr.country:
                    addr_dict["country"] = addr.country
                if addr.postal_code:
                    addr_dict["postalCode"] = addr.postal_code
                if addr.state_or_province:
                    addr_dict["stateOrProvince"] = addr.state_or_province
                if addr.address_line1:
                    addr_dict["addressLine1"] = addr.address_line1
                if addr.address_line2:
                    addr_dict["addressLine2"] = addr.address_line2
                if addr.address_line3:
                    addr_dict["addressLine3"] = addr.address_line3
                if addr_dict:
                    user_dict["deliveryAddress"] = addr_dict
            
            result["userInfo"] = user_dict
        
        if self.store_info and self.store_info.mcc:
            result["storeInfo"] = {"MCC": self.store_info.mcc}
        
        if self.return_url:
            result["returnUrl"] = self.return_url
        
        if self.webhook:
            result["webhook"] = self.webhook
        
        if self.valid_time is not None:
            result["validTime"] = self.valid_time
        
        return result


@dataclass
class LinkPayOrderResponse:
    """创建 LinkPay 订单响应"""
    result: Result
    link_url: Optional[str] = None
    expiry_time: Optional[str] = None  # RFC3339格式
    merchant_order_info: Optional[MerchantOrderInfo] = None
    trans_amount: Optional[TransAmount] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LinkPayOrderResponse':
        """从字典创建响应对象"""
        result = Result(
            code=data["result"]["code"],
            message=data["result"]["message"]
        )
        
        link_url = data.get("linkUrl")
        expiry_time = data.get("expiryTime")
        
        merchant_order_info = None
        if "merchantOrderInfo" in data:
            order_data = data["merchantOrderInfo"]
            merchant_order_info = MerchantOrderInfo(
                merchant_order_id=order_data["merchantOrderID"],
                merchant_order_time="",  # 响应中不包含时间
                status=OrderStatus(order_data["status"]) if "status" in order_data else None
            )
        
        trans_amount = None
        if "transAmount" in data:
            amount_data = data["transAmount"]
            trans_amount = TransAmount(
                currency=amount_data["currency"],
                value=amount_data["value"]
            )
        
        return cls(
            result=result,
            link_url=link_url,
            expiry_time=expiry_time,
            merchant_order_info=merchant_order_info,
            trans_amount=trans_amount
        )


# ============================================================================
# LinkPay Order Query Response Model
# ============================================================================

@dataclass
class LinkPayOrderQueryResponse:
    """查询 LinkPay 订单响应"""
    result: Result
    merchant_order_info: Optional[MerchantOrderInfo] = None
    payment_method: Optional[PaymentMethod] = None
    transaction_info: Optional[TransactionInfo] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LinkPayOrderQueryResponse':
        """从字典创建查询响应对象"""
        result = Result(
            code=data["result"]["code"],
            message=data["result"]["message"]
        )
        
        merchant_order_info = None
        if "merchantOrderInfo" in data:
            order_data = data["merchantOrderInfo"]
            merchant_order_info = MerchantOrderInfo(
                merchant_order_id=order_data["merchantOrderID"],
                merchant_order_time="",  # 查询响应中不包含时间
                status=OrderStatus(order_data["status"]) if "status" in order_data else None,
                related_transactions=order_data.get("relatedTransactions")
            )
        
        # TODO: 实现 PaymentMethod 和 TransactionInfo 的解析
        # 这些将在后续实现中完善
        
        return cls(
            result=result,
            merchant_order_info=merchant_order_info,
            payment_method=None,  # 待实现
            transaction_info=None  # 待实现
        )


# ============================================================================
# LinkPay Refund Request/Response Models
# ============================================================================

@dataclass
class RefundReason(str, Enum):
    """退款原因枚举"""
    DUPLICATE = "duplicate"
    FRAUDULENT = "fraudulent"
    REQUESTED_BY_CUSTOMER = "requested_by_customer"
    EXPIRED_UNCAPTURED = "expired_uncaptured"
    OTHER = "other"


@dataclass
class RefundStatus(str, Enum):
    """退款状态枚举"""
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    REQUIRES_ACTION = "requires_action"


@dataclass
class LinkPayRefundRequest:
    """创建 LinkPay 退款请求"""
    merchant_trans_id: str  # 商户退款交易ID，最大32位
    merchant_trans_time: str  # 退款交易时间，RFC3339格式
    refund_amount: TransAmount  # 退款金额
    reason: Optional[RefundReason] = None  # 退款原因
    description: Optional[str] = None  # 退款描述，最大255字符
    metadata: Optional[Dict[str, str]] = None  # 元数据
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于API请求"""
        result = {
            "merchantTransID": self.merchant_trans_id,
            "merchantTransTime": self.merchant_trans_time,
            "refundAmount": {
                "currency": self.refund_amount.currency,
                "value": self.refund_amount.value
            }
        }
        
        if self.reason:
            result["reason"] = self.reason.value
        
        if self.description:
            result["description"] = self.description
        
        if self.metadata:
            result["metadata"] = self.metadata
        
        return result


@dataclass
class LinkPayRefundResponse:
    """创建 LinkPay 退款响应"""
    result: Result
    refund_id: Optional[str] = None  # EVO Cloud 退款ID
    merchant_trans_id: Optional[str] = None  # 商户退款交易ID
    refund_amount: Optional[TransAmount] = None  # 退款金额
    status: Optional[RefundStatus] = None  # 退款状态
    created_time: Optional[str] = None  # 创建时间，RFC3339格式
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LinkPayRefundResponse':
        """从字典创建响应对象"""
        result = Result(
            code=data["result"]["code"],
            message=data["result"]["message"]
        )
        
        refund_id = data.get("refundID")
        merchant_trans_id = data.get("merchantTransID")
        
        refund_amount = None
        if "refundAmount" in data:
            amount_data = data["refundAmount"]
            refund_amount = TransAmount(
                currency=amount_data["currency"],
                value=amount_data["value"]
            )
        
        status = None
        if "status" in data:
            status = RefundStatus(data["status"])
        
        created_time = data.get("createdTime")
        
        return cls(
            result=result,
            refund_id=refund_id,
            merchant_trans_id=merchant_trans_id,
            refund_amount=refund_amount,
            status=status,
            created_time=created_time
        )


@dataclass
class LinkPayRefundQueryResponse:
    """查询 LinkPay 退款响应"""
    result: Result
    refund_id: Optional[str] = None  # EVO Cloud 退款ID
    merchant_trans_id: Optional[str] = None  # 商户退款交易ID
    original_merchant_order_id: Optional[str] = None  # 原始订单ID
    refund_amount: Optional[TransAmount] = None  # 退款金额
    status: Optional[RefundStatus] = None  # 退款状态
    reason: Optional[RefundReason] = None  # 退款原因
    description: Optional[str] = None  # 退款描述
    created_time: Optional[str] = None  # 创建时间，RFC3339格式
    updated_time: Optional[str] = None  # 更新时间，RFC3339格式
    failure_reason: Optional[str] = None  # 失败原因
    metadata: Optional[Dict[str, str]] = None  # 元数据
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LinkPayRefundQueryResponse':
        """从字典创建查询响应对象"""
        result = Result(
            code=data["result"]["code"],
            message=data["result"]["message"]
        )
        
        refund_id = data.get("refundID")
        merchant_trans_id = data.get("merchantTransID")
        original_merchant_order_id = data.get("originalMerchantOrderID")
        
        refund_amount = None
        if "refundAmount" in data:
            amount_data = data["refundAmount"]
            refund_amount = TransAmount(
                currency=amount_data["currency"],
                value=amount_data["value"]
            )
        
        status = None
        if "status" in data:
            status = RefundStatus(data["status"])
        
        reason = None
        if "reason" in data:
            reason = RefundReason(data["reason"])
        
        description = data.get("description")
        created_time = data.get("createdTime")
        updated_time = data.get("updatedTime")
        failure_reason = data.get("failureReason")
        metadata = data.get("metadata")
        
        return cls(
            result=result,
            refund_id=refund_id,
            merchant_trans_id=merchant_trans_id,
            original_merchant_order_id=original_merchant_order_id,
            refund_amount=refund_amount,
            status=status,
            reason=reason,
            description=description,
            created_time=created_time,
            updated_time=updated_time,
            failure_reason=failure_reason,
            metadata=metadata
        )


# ============================================================================
# Utility Functions
# ============================================================================

def validate_merchant_order_id(order_id: str) -> bool:
    """验证商户订单ID格式"""
    if not order_id or len(order_id) > 32:
        return False
    # 只允许字母和数字
    return order_id.replace('_', '').replace('-', '').isalnum()


def validate_currency_code(currency: str) -> bool:
    """验证货币代码格式"""
    return len(currency) == 3 and currency.isalpha() and currency.isupper()


def validate_amount_value(value: str) -> bool:
    """验证金额格式"""
    try:
        float_val = float(value)
        return float_val > 0 and len(value) <= 12
    except ValueError:
        return False


# ============================================================================
# Utility Functions for Refund
# ============================================================================

def validate_merchant_trans_id(trans_id: str) -> bool:
    """验证商户交易ID格式"""
    if not trans_id or len(trans_id) > 32:
        return False
    # 只允许字母、数字、下划线和连字符
    return trans_id.replace('_', '').replace('-', '').isalnum()


def validate_refund_description(description: str) -> bool:
    """验证退款描述格式"""
    return len(description) <= 255 if description else True
