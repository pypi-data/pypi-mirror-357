"""
Data models for The Odds API.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Union

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


@dataclass(frozen=True)
class Sport:
    """Represents a sport available in The Odds API."""
    
    key: str
    group: str
    title: str
    description: str
    active: bool
    has_outrights: bool


@dataclass(frozen=True)
class Outcome:
    """Represents a betting outcome with odds."""
    
    name: str
    price: Union[float, int]
    point: Optional[float] = None
    description: Optional[str] = None
    link: Optional[str] = None
    sid: Optional[str] = None
    bet_limit: Optional[float] = None


@dataclass(frozen=True)
class Market:
    """Represents a betting market (e.g., h2h, spreads, totals)."""
    
    key: str
    outcomes: List[Outcome]
    last_update: Optional[datetime] = None
    link: Optional[str] = None
    sid: Optional[str] = None


@dataclass(frozen=True)
class Bookmaker:
    """Represents a bookmaker with their markets."""
    
    key: str
    title: str
    last_update: Optional[datetime]
    markets: List[Market]
    link: Optional[str] = None
    sid: Optional[str] = None


@dataclass(frozen=True)
class Score:
    """Represents team scores in a completed or live game."""
    
    name: str
    score: Optional[Union[str, int]] = None


@dataclass(frozen=True)
class Participant:
    """Represents a participant (team or individual) in a sport."""
    
    id: str
    full_name: str


@dataclass(frozen=True)
class Event:
    """Represents a sports event with odds from various bookmakers."""
    
    id: str
    sport_key: str
    sport_title: str
    commence_time: datetime
    home_team: Optional[str]
    away_team: Optional[str]
    bookmakers: List[Bookmaker]


@dataclass(frozen=True)
class EventScore:
    """Represents a sports event with scores (for live and completed games)."""
    
    id: str
    sport_key: str
    sport_title: str
    commence_time: datetime
    completed: bool
    home_team: Optional[str]
    away_team: Optional[str]
    scores: Optional[List[Score]] = None
    last_update: Optional[datetime] = None


@dataclass(frozen=True)
class EventWithoutOdds:
    """Represents a sports event without odds (from /events endpoint)."""
    
    id: str
    sport_key: str
    sport_title: str
    commence_time: datetime
    home_team: Optional[str]
    away_team: Optional[str]


@dataclass(frozen=True)
class HistoricalSnapshot:
    """Represents a historical data snapshot with timestamp information."""
    
    timestamp: datetime
    previous_timestamp: Optional[datetime]
    next_timestamp: Optional[datetime]
    data: Union[List[Event], List[EventWithoutOdds], Event]


# Type aliases for common parameter types
Region = Literal["us", "us2", "uk", "us_dfs", "au", "eu"]
MarketType = Literal["h2h", "h2h_lay", "spreads", "totals", "outrights"]
OddsFormat = Literal["decimal", "american"]
DateFormat = Literal["iso", "unix"] 

