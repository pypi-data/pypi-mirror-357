"""
Custom exceptions for the ESRI Converter package.

This module defines all custom exceptions used throughout the package
to provide clear error handling and debugging information.
"""

from typing import Any


class ESRIConverterError(Exception):
    """Base exception for all ESRI Converter errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} (Details: {details_str})"
        return self.message


class UnsupportedFormatError(ESRIConverterError):
    """Raised when an unsupported file format is encountered."""

    def __init__(
        self,
        format_name: str,
        supported_formats: list[str] | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        supported = supported_formats or []
        message = f"Unsupported format: {format_name}"
        if supported:
            message += f". Supported formats: {', '.join(supported)}"

        super().__init__(message, details)
        self.format_name = format_name
        self.supported_formats = supported


class ValidationError(ESRIConverterError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, details)
        self.field = field
        self.value = value


class ConversionError(ESRIConverterError):
    """Raised when a conversion operation fails."""

    def __init__(
        self,
        message: str,
        source_file: str | None = None,
        target_file: str | None = None,
        layer_name: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, details)
        self.source_file = source_file
        self.target_file = target_file
        self.layer_name = layer_name


class SchemaError(ConversionError):
    """Raised when schema-related issues occur during conversion."""

    def __init__(
        self,
        message: str,
        schema_info: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.schema_info = schema_info or {}


class MemoryError(ConversionError):
    """Raised when memory-related issues occur during conversion."""

    def __init__(
        self,
        message: str,
        memory_usage: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.memory_usage = memory_usage or {}


class FileAccessError(ESRIConverterError):
    """Raised when file access issues occur."""

    def __init__(
        self,
        message: str,
        file_path: str | None = None,
        operation: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, details)
        self.file_path = file_path
        self.operation = operation
