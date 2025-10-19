class PositionTrackerException(Exception):
    """Base exception for this application."""
    pass

class PortfolioNotFound(PositionTrackerException):
    """Raised when portfolio data for a user is not found."""
    pass