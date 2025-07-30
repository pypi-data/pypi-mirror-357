"""
EVO Cloud API Base Client

Base client implementation for EVO Cloud API with core functionality.
"""

import json
import logging
import requests
from typing import Optional, Dict, Any, Union
from urllib.parse import urljoin, quote
from datetime import datetime, timezone

from .signature import SignatureGenerator, SignType
from .exceptions import APIException, ValidationException

# Set up logger
logger = logging.getLogger(__name__)


class BaseClient:
    """
    EVO Cloud API Base Client
    
    This is the base client that handles core interactions with the EVO Cloud API,
    including signature generation, request formatting, and response parsing.
    
    For LinkPay-specific functionality, use evocloud_sdk.linkpay.LinkPayClient.
    """
    
    def __init__(
        self,
        base_url: str,
        sign_key: str,
        sign_type: SignType = SignType.SHA256,
        timeout: int = 60,
        max_retries: int = 1
    ):
        """
        Initialize the EVO Cloud client.
        
        Args:
            base_url: EVO Cloud API base URL (e.g., "https://online-uat.everonet.com")
            sid: System ID assigned by EVO Cloud
            sign_key: Signing key assigned by EVO Cloud
            sign_type: Signature algorithm to use
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        if not base_url:
            raise ValidationException("Base URL cannot be None or empty")
        if not sign_key:
            raise ValidationException("Sign key cannot be None or empty")
            
        self.base_url = base_url.rstrip('/')
        self.signature_generator = SignatureGenerator(sign_key, sign_type)
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'EvoCloud-Python-SDK/2.0.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Configure logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        if not logger.handlers:
            root_logger = logging.getLogger()
            if not root_logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
                logger.addHandler(handler)
                logger.propagate = False
            else:
                logger.propagate = True
            
            logger.setLevel(logging.INFO)
    
    
    def set_log_level(self, level: int):
        """Set the logging level for the client."""
        logger.setLevel(level)
    
    def enable_debug_logging(self):
        """Enable debug level logging"""
        self.set_log_level(logging.DEBUG)
    
    def disable_debug_logging(self):
        """Disable debug logging (set to INFO level)"""
        self.set_log_level(logging.INFO)
    
    def _make_request(
        self,
        method: str,
        url_path: str,
        data: Optional[Dict[str, Any]] = None,
        path_params: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to the EVO Cloud API.
        
        Args:
            method: HTTP method
            url_path: API endpoint with placeholders
            data: Request payload
            path_params: Path parameters to replace in endpoint
            
        Returns:
            Parsed response data
            
        Raises:
            APIException: If the API request fails
        """
        # Replace path parameters in endpoint
        if path_params:
            for key, value in path_params.items():
                endpoint = endpoint.replace(f"{{{key}}}", quote(str(value), safe=''))
        
        # Build URL path
        full_url = urljoin(self.base_url, url_path)
        
        # Prepare request body
        body_json = ""
        if data:
            body_json = json.dumps(data, separators=(',', ':'), default=str)
        
        # Generate headers with signature
        headers = self.signature_generator.generate_headers(
            method.upper(),
            url_path,
            body_json
        )
        
        # Merge with session headers
        request_headers = {**self.session.headers, **headers}
        
        # Log request details
        logger.info(f"Making {method.upper()} request to EVO Cloud API: {full_url} ")
        
        # Make request with retries
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(
                        full_url,
                        headers=request_headers,
                        timeout=self.timeout
                    )
                else:
                    response = self.session.request(
                        method.upper(),
                        full_url,
                        headers=request_headers,
                        data=body_json.encode('utf-8') if body_json else None,
                        timeout=self.timeout
                    )
                
                # Log response details
                logger.info(f"Response Status: {response.status_code}")
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"Response Headers: {dict(response.headers)}")
                    logger.debug(f"Response Body: {response.text}")
                
                # Check for HTTP errors
                if response.status_code >= 400:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    raise APIException(error_msg, response.status_code)
                
                # Parse JSON response
                try:
                    response_data = response.json()
                except json.JSONDecodeError as e:
                    error_msg = f"Invalid JSON response: {e}"
                    logger.error(error_msg)
                    raise APIException(error_msg)
                
                # Check API result code
                if 'result' in response_data:
                    result = response_data['result']
                    if result.get('code') != 'S0000':
                        error_msg = f"API Error {result.get('code')}: {result.get('message')}"
                        logger.error(error_msg)
                        raise APIException(error_msg, result.get('code'))
                
                logger.info("Request completed successfully")
                return response_data
                
            except (requests.exceptions.RequestException, APIException) as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries + 1}), retrying in {wait_time}s: {e}")
                    import time
                    time.sleep(wait_time)
                else:
                    logger.error(f"Request failed after {self.max_retries + 1} attempts: {e}")
                    break
        
        # If we get here, all retries failed
        if isinstance(last_exception, APIException):
            raise last_exception
        else:
            raise APIException(f"Request failed: {last_exception}")
    
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

