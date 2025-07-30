from ..common import BaseClient, SignType


class MerchantClient(BaseClient):
    def __init__(self, base_url: str, sid: str, sign_key: str, sign_type: SignType = SignType.SHA256, timeout: int = 60, max_retries: int = 1):
        super().__init__(base_url, sign_key, sign_type, timeout, max_retries)
        self.sid = sid
