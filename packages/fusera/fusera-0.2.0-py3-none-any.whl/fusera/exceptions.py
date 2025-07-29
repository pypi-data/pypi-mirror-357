# ABOUTME: Custom exception classes for Fusera SDK
# ABOUTME: Provides specific error types for better error handling and user guidance

"""Custom exceptions for Fusera SDK"""

class FuseraError(Exception):
    """Base exception for Fusera SDK"""
    pass

class APIKeyError(FuseraError):
    """API key related errors"""
    pass

class UploadError(FuseraError):
    """Model upload errors"""
    pass

class FileTooLargeError(FuseraError):
    """Model exceeds size limit"""
    pass