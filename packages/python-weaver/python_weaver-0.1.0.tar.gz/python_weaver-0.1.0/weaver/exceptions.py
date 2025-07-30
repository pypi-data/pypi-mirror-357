"""
Custom exceptions used throughout python-weaver.
"""

class WeaverError(Exception):
    """Base exception for python-weaver"""
    pass

class DatabaseError(WeaverError):
    """Raised for database-related errors"""
    pass

class ConnectorError(WeaverError):
    """Raised when source ingestion fails"""
    pass