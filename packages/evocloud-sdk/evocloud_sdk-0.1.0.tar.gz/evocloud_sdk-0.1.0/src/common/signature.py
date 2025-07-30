"""
EVO Cloud API Signature Generator

Implements the signature generation and validation logic as per EVO Cloud API documentation.
"""

import hashlib
import hmac
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from .exceptions import SignatureException


class SignType(Enum):
    """Supported signature algorithms"""
    SHA256 = "SHA256"
    SHA512 = "SHA512"
    HMAC_SHA256 = "HMAC-SHA256"
    HMAC_SHA512 = "HMAC-SHA512"


class SignatureGenerator:
    """
    Generates and validates signatures for EVO Cloud API requests and responses.
    """
    
    def __init__(self, sign_key: str, sign_type: SignType = SignType.SHA256):
        """
        Initialize signature generator.
        
        Args:
            sign_key: The signing key assigned by EVO Cloud
            sign_type: The signature algorithm to use
        """
        if not sign_key:
            raise SignatureException("Sign key cannot be None or empty")
        self.sign_key = sign_key
        self.sign_type = sign_type
    
    def generate_msg_id(self) -> str:
        """
        Generate a unique message ID (UUID without hyphens).
        
        Returns:
            A 32-character UUID string
        """
        return str(uuid.uuid4()).replace('-', '')
    
    def generate_datetime(self) -> str:
        """
        Generate current datetime in EVO Cloud format.
        
        Returns:
            Datetime string in format: YYYY-MM-DDThh:mm:ss+hh:00
        """
        now = datetime.now(timezone.utc)
        # Convert to +08:00 timezone (as shown in examples)
        from datetime import timedelta
        beijing_time = now + timedelta(hours=8)
        return beijing_time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
    
    def build_signature_string(
        self,
        http_method: str,
        url_path: str,
        datetime_str: str,
        msg_id: str,
        http_body: str = ""
    ) -> str:
        """
        Build the signature string according to EVO Cloud specification.
        
        Args:
            http_method: HTTP method (GET, POST, PUT, DELETE)
            url_path: URL path + query parameters
            datetime_str: Request datetime
            msg_id: Message ID
            http_body: HTTP request body (empty for GET requests)
            
        Returns:
            The signature string to be signed
        """
        components = [
            http_method.upper(),
            url_path,
            datetime_str,
            self.sign_key,
            msg_id
        ]
        
        # Add HTTP body if present (not for GET requests)
        if http_body:
            components.append(http_body)
        
        return '\n'.join(components)
    
    def calculate_signature(self, signature_string: str) -> str:
        """
        Calculate the signature based on the signature string and algorithm.
        
        Args:
            signature_string: The string to be signed
            
        Returns:
            The calculated signature
            
        Raises:
            SignatureException: If signature calculation fails
        """
        try:
            if self.sign_type == SignType.SHA256:
                return hashlib.sha256(signature_string.encode('utf-8')).hexdigest()
            
            elif self.sign_type == SignType.SHA512:
                return hashlib.sha512(signature_string.encode('utf-8')).hexdigest()
            
            elif self.sign_type == SignType.HMAC_SHA256:
                return hmac.new(
                    self.sign_key.encode('utf-8'),
                    signature_string.encode('utf-8'),
                    hashlib.sha256
                ).hexdigest().upper()
            
            elif self.sign_type == SignType.HMAC_SHA512:
                return hmac.new(
                    self.sign_key.encode('utf-8'),
                    signature_string.encode('utf-8'),
                    hashlib.sha512
                ).hexdigest().upper()
            
            else:
                raise SignatureException(f"Unsupported signature type: {self.sign_type}")
                
        except Exception as e:
            raise SignatureException(f"Failed to calculate signature: {str(e)}")
    
    def generate_signature(
        self,
        http_method: str,
        url_path: str,
        datetime_str: str,
        msg_id: str,
        http_body: str = ""
    ) -> str:
        """
        Generate signature for a request.
        
        Args:
            http_method: HTTP method
            url_path: URL path + query parameters
            datetime_str: Request datetime
            msg_id: Message ID
            http_body: HTTP request body
            
        Returns:
            The generated signature
        """
        signature_string = self.build_signature_string(
            http_method, url_path, datetime_str, msg_id, http_body
        )
        return self.calculate_signature(signature_string)
    
    def verify_signature(
        self,
        expected_signature: str,
        http_method: str,
        url_path: str,
        datetime_str: str,
        msg_id: str,
        http_body: str = ""
    ) -> bool:
        """
        Verify a signature against expected value.
        
        Args:
            expected_signature: The signature to verify against
            http_method: HTTP method
            url_path: URL path + query parameters
            datetime_str: Request datetime
            msg_id: Message ID
            http_body: HTTP request body
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            calculated_signature = self.generate_signature(
                http_method, url_path, datetime_str, msg_id, http_body
            )
            return calculated_signature.lower() == expected_signature.lower()
        except Exception:
            return False
    
    def generate_headers(
        self,
        http_method: str,
        url_path: str,
        http_body: str = "",
        datetime_str: Optional[str] = None,
        msg_id: Optional[str] = None
    ) -> dict:
        """
        Generate complete HTTP headers including signature.
        
        Args:
            http_method: HTTP method
            url_path: URL path + query parameters
            http_body: HTTP request body
            datetime_str: Request datetime (auto-generated if not provided)
            msg_id: Message ID (auto-generated if not provided)
            
        Returns:
            Dictionary of HTTP headers
        """
        if datetime_str is None:
            datetime_str = self.generate_datetime()
        
        if msg_id is None:
            msg_id = self.generate_msg_id()
        
        signature = self.generate_signature(
            http_method, url_path, datetime_str, msg_id, http_body
        )
        
        return {
            'Authorization': signature,
            'Content-Type': 'application/json',
            'DateTime': datetime_str,
            'MsgID': msg_id,
            'SignType': self.sign_type.value
        } 