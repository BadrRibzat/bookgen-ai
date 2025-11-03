"""
Custom exception handler for consistent error responses.
Implements structured error format across all APIs.
"""

from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import ValidationError, AuthenticationFailed, NotFound
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import PermissionDenied
from django.http import Http404
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns structured error responses.
    
    Response format:
    {
        "success": false,
        "error": {
            "code": "ERROR_CODE",
            "message": "User-friendly error message",
            "details": {...}  # Optional, for validation errors
        }
    }
    """
    
    # Call DRF's default exception handler first
    response = drf_exception_handler(exc, context)
    
    # If DRF didn't handle it, handle it ourselves
    if response is None:
        return handle_unhandled_exception(exc, context)
    
    # Transform the response to our structured format
    error_data = {
        'success': False,
        'error': {
            'code': get_error_code(exc),
            'message': get_error_message(exc),
        }
    }
    
    # Add validation details if present
    if isinstance(exc, ValidationError) and hasattr(exc, 'detail'):
        error_data['error']['details'] = exc.detail
    
    # Log error for monitoring
    log_error(exc, context, response.status_code)
    
    return Response(error_data, status=response.status_code)


def handle_unhandled_exception(exc, context):
    """Handle exceptions not caught by DRF."""
    
    # Django's Http404
    if isinstance(exc, Http404):
        error_data = {
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'The requested resource was not found.',
            }
        }
        logger.warning(f"404 Not Found: {exc}", extra={'context': context})
        return Response(error_data, status=status.HTTP_404_NOT_FOUND)
    
    # Django's PermissionDenied
    if isinstance(exc, PermissionDenied):
        error_data = {
            'success': False,
            'error': {
                'code': 'PERMISSION_DENIED',
                'message': 'You do not have permission to perform this action.',
            }
        }
        logger.warning(f"Permission Denied: {exc}", extra={'context': context})
        return Response(error_data, status=status.HTTP_403_FORBIDDEN)
    
    # Log unhandled exception
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
        exc_info=True,
        extra={'context': context}
    )
    
    # Generic server error
    error_data = {
        'success': False,
        'error': {
            'code': 'SERVER_ERROR',
            'message': 'An unexpected error occurred. Please try again later.',
        }
    }
    return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_error_code(exc):
    """Determine error code based on exception type."""
    
    error_code_map = {
        'ValidationError': 'VALIDATION_ERROR',
        'AuthenticationFailed': 'AUTHENTICATION_FAILED',
        'NotAuthenticated': 'NOT_AUTHENTICATED',
        'PermissionDenied': 'PERMISSION_DENIED',
        'NotFound': 'NOT_FOUND',
        'MethodNotAllowed': 'METHOD_NOT_ALLOWED',
        'Throttled': 'RATE_LIMIT_EXCEEDED',
        'ParseError': 'PARSE_ERROR',
    }
    
    exc_name = type(exc).__name__
    return error_code_map.get(exc_name, 'UNKNOWN_ERROR')


def get_error_message(exc):
    """Extract user-friendly error message from exception."""
    
    # For validation errors, use the first error message
    if isinstance(exc, ValidationError):
        if isinstance(exc.detail, dict):
            # Get first field's first error
            for field, errors in exc.detail.items():
                if isinstance(errors, list) and errors:
                    return str(errors[0])
                return str(errors)
        elif isinstance(exc.detail, list) and exc.detail:
            return str(exc.detail[0])
    
    # Use default detail if available
    if hasattr(exc, 'detail'):
        return str(exc.detail)
    
    # Fallback to exception message
    return str(exc)


def log_error(exc, context, status_code):
    """Log error with context for monitoring."""
    
    # Get request info
    request = context.get('request')
    view = context.get('view')
    
    log_data = {
        'exception': type(exc).__name__,
        'error_message': str(exc),
        'status_code': status_code,
        'path': request.path if request else None,
        'method': request.method if request else None,
        'user': request.user.email if request and request.user.is_authenticated else 'Anonymous',
        'view': view.__class__.__name__ if view else None,
    }
    
    # Log at appropriate level
    if status_code >= 500:
        logger.error("Server error", extra=log_data, exc_info=True)
    elif status_code >= 400:
        logger.warning("Client error", extra=log_data)
    else:
        logger.info("Request completed with error", extra=log_data)
