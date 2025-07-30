import os
from .common import SignType
from .linkpay.client import LinkpayClient
from .merchant.client import MerchantClient


class EVOCloudClient():
    def __init__(self, base_url: str, sign_key: str = None,  sid: str = None, sign_type: SignType = SignType.SHA256, timeout: int = 60, max_retries: int = 1):
        self.base_url = base_url if base_url else os.getenv("EVOCLOUD_BASE_URL")
        self.sid = sid if sid else os.getenv("EVOCLOUD_SID")
        self.sign_key = sign_key if sign_key else os.getenv("EVOCLOUD_SIGN_KEY")
        self.sign_type = sign_type if sign_type else SignType.SHA256
        self.timeout = timeout
        self.max_retries = max_retries

        # 聚合client
        self.linkpay = LinkpayClient(base_url, self.sid, self.sign_key, self.sign_type, self.timeout, self.max_retries)
        self.merchant = MerchantClient(base_url, self.sid, self.sign_key, self.sign_type, self.timeout, self.max_retries)
    