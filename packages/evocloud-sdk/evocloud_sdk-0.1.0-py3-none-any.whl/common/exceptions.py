"""
EVO Cloud SDK Exceptions
"""


class EVOCloudException(Exception):
    """Base exception for EVO Cloud SDK"""
    pass


class SignatureException(EVOCloudException):
    """Exception raised when signature generation or validation fails"""
    pass


class APIException(EVOCloudException):
    """Exception raised when API call fails"""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(message)


class ValidationException(EVOCloudException):
    """Exception raised when request validation fails"""
    pass 