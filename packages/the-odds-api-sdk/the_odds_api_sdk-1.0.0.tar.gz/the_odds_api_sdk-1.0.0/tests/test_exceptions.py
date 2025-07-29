"""
Unit tests for The Odds API exceptions.
"""

import pytest
from the_odds_api_sdk.exceptions import (
    OddsAPIError,
    OddsAPIAuthError,
    OddsAPIUsageLimitError,
    OddsAPIValidationError,
    OddsAPIRateLimitError,
    OddsAPINotFoundError,
    OddsAPIServerError,
)


class TestExceptions:
    """Test cases for exception classes."""
    
    def test_base_odds_api_error(self):
        """Test base OddsAPIError exception."""
        error = OddsAPIError("Test error message", status_code=400)
        
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.status_code == 400
        
        # Test without status code
        error_no_code = OddsAPIError("No status code")
        assert error_no_code.message == "No status code"
        assert error_no_code.status_code is None
    
    def test_auth_error(self):
        """Test OddsAPIAuthError exception."""
        # Test with default message
        error = OddsAPIAuthError()
        assert str(error) == "Invalid API key"
        assert error.message == "Invalid API key"
        assert error.status_code == 401
        
        # Test with custom message
        error_custom = OddsAPIAuthError("Custom auth message")
        assert str(error_custom) == "Custom auth message"
        assert error_custom.message == "Custom auth message"
        assert error_custom.status_code == 401
    
    def test_usage_limit_error(self):
        """Test OddsAPIUsageLimitError exception."""
        # Test with default message
        error = OddsAPIUsageLimitError()
        assert str(error) == "API usage limit exceeded"
        assert error.message == "API usage limit exceeded"
        assert error.status_code == 401
        
        # Test with custom message
        error_custom = OddsAPIUsageLimitError("Custom usage limit message")
        assert str(error_custom) == "Custom usage limit message"
        assert error_custom.message == "Custom usage limit message"
        assert error_custom.status_code == 401
    
    def test_validation_error(self):
        """Test OddsAPIValidationError exception."""
        # Test with default message
        error = OddsAPIValidationError()
        assert str(error) == "Invalid query parameters"
        assert error.message == "Invalid query parameters"
        assert error.status_code == 422
        
        # Test with custom message
        error_custom = OddsAPIValidationError("Custom validation message")
        assert str(error_custom) == "Custom validation message"
        assert error_custom.message == "Custom validation message"
        assert error_custom.status_code == 422
    
    def test_rate_limit_error(self):
        """Test OddsAPIRateLimitError exception."""
        # Test with default message
        error = OddsAPIRateLimitError()
        assert str(error) == "Rate limit exceeded"
        assert error.message == "Rate limit exceeded"
        assert error.status_code == 429
        
        # Test with custom message
        error_custom = OddsAPIRateLimitError("Custom rate limit message")
        assert str(error_custom) == "Custom rate limit message"
        assert error_custom.message == "Custom rate limit message"
        assert error_custom.status_code == 429
    
    def test_not_found_error(self):
        """Test OddsAPINotFoundError exception."""
        # Test with default message
        error = OddsAPINotFoundError()
        assert str(error) == "Resource not found"
        assert error.message == "Resource not found"
        assert error.status_code == 404
        
        # Test with custom message
        error_custom = OddsAPINotFoundError("Custom not found message")
        assert str(error_custom) == "Custom not found message"
        assert error_custom.message == "Custom not found message"
        assert error_custom.status_code == 404
    
    def test_server_error(self):
        """Test OddsAPIServerError exception."""
        # Test with default message
        error = OddsAPIServerError()
        assert str(error) == "Server error"
        assert error.message == "Server error"
        assert error.status_code == 500
        
        # Test with custom message
        error_custom = OddsAPIServerError("Custom server error message")
        assert str(error_custom) == "Custom server error message"
        assert error_custom.message == "Custom server error message"
        assert error_custom.status_code == 500
    
    def test_exception_inheritance(self):
        """Test that all exceptions inherit from the base exception."""
        # Test that all custom exceptions inherit from OddsAPIError
        assert issubclass(OddsAPIAuthError, OddsAPIError)
        assert issubclass(OddsAPIUsageLimitError, OddsAPIError)
        assert issubclass(OddsAPIValidationError, OddsAPIError)
        assert issubclass(OddsAPIRateLimitError, OddsAPIError)
        assert issubclass(OddsAPINotFoundError, OddsAPIError)
        assert issubclass(OddsAPIServerError, OddsAPIError)
        
        # Test that base exception inherits from Python's Exception
        assert issubclass(OddsAPIError, Exception)
    
    def test_exception_raising(self):
        """Test that exceptions can be raised properly."""
        # Test raising each exception type
        with pytest.raises(OddsAPIError):
            raise OddsAPIError("Test base error")
        
        with pytest.raises(OddsAPIAuthError):
            raise OddsAPIAuthError("Test auth error")
        
        with pytest.raises(OddsAPIUsageLimitError):
            raise OddsAPIUsageLimitError("Test usage limit error")
        
        with pytest.raises(OddsAPIValidationError):
            raise OddsAPIValidationError("Test validation error")
        
        with pytest.raises(OddsAPIRateLimitError):
            raise OddsAPIRateLimitError("Test rate limit error")
        
        with pytest.raises(OddsAPINotFoundError):
            raise OddsAPINotFoundError("Test not found error")
        
        with pytest.raises(OddsAPIServerError):
            raise OddsAPIServerError("Test server error")
    
    def test_exception_catching_as_base_class(self):
        """Test that specific exceptions can be caught as base OddsAPIError."""
        # Test that specific exceptions can be caught as the base exception
        with pytest.raises(OddsAPIError):
            raise OddsAPIAuthError("Auth error")
        
        with pytest.raises(OddsAPIError):
            raise OddsAPIRateLimitError("Rate limit error")
        
        with pytest.raises(OddsAPIError):
            raise OddsAPIServerError("Server error")
    
    def test_exception_attributes_preservation(self):
        """Test that exception attributes are preserved when caught."""
        try:
            raise OddsAPIRateLimitError("Custom rate limit message")
        except OddsAPIError as e:
            assert e.message == "Custom rate limit message"
            assert e.status_code == 429
            assert isinstance(e, OddsAPIRateLimitError)
        
        try:
            raise OddsAPIValidationError("Custom validation message")
        except OddsAPIError as e:
            assert e.message == "Custom validation message"
            assert e.status_code == 422
            assert isinstance(e, OddsAPIValidationError) 