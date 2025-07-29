"""
The Odds API SDK - Elegant Python client for The Odds API.
"""

from .client import OddsAPIClient
from .exceptions import (
    OddsAPIError,
    OddsAPIAuthError,
    OddsAPIUsageLimitError,
    OddsAPIValidationError,
    OddsAPINotFoundError,
    OddsAPIRateLimitError,
    OddsAPIServerError,
)
from .models import (
    Bookmaker,
    DateFormat,
    Event,
    EventScore,
    EventWithoutOdds,
    HistoricalSnapshot,
    Market,
    MarketType,
    OddsFormat,
    Outcome,
    Participant,
    Region,
    Score,
    Sport,
)

__version__ = "1.0.0"
__all__ = [
    "OddsAPIClient",
    "OddsAPIError",
    "OddsAPIAuthError",
    "OddsAPIUsageLimitError",
    "OddsAPIValidationError", 
    "OddsAPINotFoundError",
    "OddsAPIRateLimitError",
    "OddsAPIServerError",
    "Bookmaker",
    "DateFormat",
    "Event",
    "EventScore",
    "EventWithoutOdds",
    "HistoricalSnapshot",
    "Market",
    "MarketType",
    "OddsFormat",
    "Outcome",
    "Participant",
    "Region",
    "Score",
    "Sport",
] 