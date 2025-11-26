"""Custom exceptions for the banking API"""


class DomainError(Exception):
    """Base domain error - maps to 400 Bad Request"""
    pass


class NotFoundError(Exception):
    """Resource not found - maps to 404 Not Found"""
    pass


class ValidationError(Exception):
    """Validation error - maps to 422 Unprocessable Entity"""
    pass


class InsufficientBalanceError(DomainError):
    """Insufficient balance for operation"""
    pass


class InvalidAccountError(DomainError):
    """Invalid account operation"""
    pass

