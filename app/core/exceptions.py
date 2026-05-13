from typing import Any


class AppException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found.", details: dict | None = None):
        super().__init__(
            code="NOT_FOUND",
            message=message,
            status_code=404,
            details=details,
        )


class ValidationException(AppException):
    def __init__(self, message: str = "Validation failed.", details: dict | None = None):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=400,
            details=details,
        )


class ConflictException(AppException):
    def __init__(self, message: str = "Resource already exists.", details: dict | None = None):
        super().__init__(
            code="RESOURCE_EXISTS",
            message=message,
            status_code=409,
            details=details,
        )