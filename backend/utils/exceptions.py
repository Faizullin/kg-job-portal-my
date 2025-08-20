from drf_standardized_errors.handler import exception_handler as standardized_exception_handler


class StandardizedViewMixin:
    """Mixin to provide standardized exception handling for DRF views."""
    
    def handle_exception(self, exc):
        response = standardized_exception_handler(exc, self.get_exception_handler_context())
        if response is None:
            return super().handle_exception(exc)
        return response


class BaseException(Exception):
    """Base exception class for the application."""
    
    def __init__(self, message="An error occurred", status_code=500, details=None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(BaseException):
    """Exception for validation errors."""
    
    def __init__(self, message="Validation error", details=None):
        super().__init__(message, status_code=400, details=details)


class PermissionException(BaseException):
    """Exception for permission errors."""
    
    def __init__(self, message="Permission denied", details=None):
        super().__init__(message, status_code=403, details=details)


class NotFoundException(BaseException):
    """Exception for not found errors."""
    
    def __init__(self, message="Resource not found", details=None):
        super().__init__(message, status_code=404, details=details)


class BusinessLogicException(BaseException):
    """Exception for business logic errors."""
    
    def __init__(self, message="Business logic error", details=None):
        super().__init__(message, status_code=422, details=details)
