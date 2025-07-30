from connections_sdk.models import ErrorResponse

class TransactionError(Exception):
    """Raised when request validation fails."""
    error_response: ErrorResponse
    def __init__(self, error_response: 'ErrorResponse'):
        self.error_response = error_response
        super().__init__(str(error_response.error_codes))

class ConfigurationError(Exception):
    """Raised when SDK configuration is invalid."""
    pass

class BasisTheoryError(Exception):
    """Raised when Basis Theory returns an error."""
    error_response: ErrorResponse
    status: int
    def __init__(self, error_response: 'ErrorResponse', status):
        self.error_response = error_response
        self.status = status
        super().__init__(str(error_response.error_codes))