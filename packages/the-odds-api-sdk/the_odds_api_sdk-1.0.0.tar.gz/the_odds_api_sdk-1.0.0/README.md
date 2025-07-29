# The Odds API Python SDK

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An unofficial Python SDK for [The Odds API](https://the-odds-api.com/).

## Features

- **Type Safe**: Full type hints and dataclass models
- **Efficient**: Minimal dependencies, smart error handling
- **Well Documented**: Extensive examples and docstrings

## Quick Start

### Installation

```bash
pip install the-odds-api-sdk
```

### Basic Usage

```python
from the_odds_api_sdk import OddsAPIClient

# Initialize client
client = OddsAPIClient(api_key="your-api-key")

# Get all sports
sports = client.get_sports()
print(f"Found {len(sports)} sports")

# Get NFL odds with enhanced features
nfl_odds = client.get_odds(
    "americanfootball_nfl", 
    regions=["us"],
    include_links=True,      # Include bookmaker links
    include_sids=True,       # Include source IDs
    include_bet_limits=True  # Include bet limits
)

for event in nfl_odds:
    print(f"{event.away_team} @ {event.home_team}")
```

## API Coverage

### Core Endpoints

#### `get_sports(all_sports=False)` → `List[Sport]`

Get available sports with option to include inactive sports.

```python
# Get only in-season sports
sports = client.get_sports()

# Get all sports including inactive ones
all_sports = client.get_sports(all_sports=True)
```

#### `get_events(sport, **options)` → `List[EventWithoutOdds]`

Get events without odds (free endpoint, doesn't count against quota).

```python
# Get all upcoming events for free
events = client.get_events("americanfootball_nfl")

# Filter by time range
from datetime import datetime, timedelta
tomorrow = datetime.now() + timedelta(days=1)
events = client.get_events(
    "americanfootball_nfl",
    commence_time_from=tomorrow
)
```

#### `get_participants(sport)` → `List[Participant]`

Get participants (teams or players) for a sport.

```python
# Get NFL teams
teams = client.get_participants("americanfootball_nfl")
for team in teams:
    print(f"{team.full_name} (ID: {team.id})")

# Get tennis players
players = client.get_participants("tennis")
```

#### `get_odds(sport, **options)` → `List[Event]`

Get odds with comprehensive filtering and enhanced features.

```python
# Enhanced odds with all features
odds = client.get_odds(
    sport="americanfootball_nfl",
    regions=["us", "uk"],
    markets=["h2h", "spreads", "totals"],
    odds_format="american",
    include_links=True,        # Bookmaker links to events/markets
    include_sids=True,         # Source IDs from bookmakers  
    include_bet_limits=True,   # Bet limits (mainly for exchanges)
    commence_time_from=datetime.now(),
    event_ids=["event1", "event2"]  # Filter specific events
)
```

#### `get_event_odds(sport, event_id, **options)` → `Event`

Get comprehensive odds for a specific event including player props.

```python
# Get all available markets for an event
event = client.get_event_odds(
    sport="americanfootball_nfl",
    event_id="event-id-123",
    regions=["us"],
    markets=["h2h", "spreads", "totals", "player_pass_tds", "player_rushing_yards"],
    include_links=True,
    include_sids=True,
    include_bet_limits=True
)
```

#### `get_scores(sport, **options)` → `List[EventScore]`

Get live and completed game scores.

```python
# Live and upcoming games only (quota cost: 1)
live_scores = client.get_scores("americanfootball_nfl")

# Include completed games from last 3 days (quota cost: 2)
all_scores = client.get_scores("americanfootball_nfl", days_from=3)

# Find completed games with scores
completed = [s for s in all_scores if s.completed and s.scores]
for game in completed:
    print(f"{game.away_team} @ {game.home_team}")
    for score in game.scores:
        print(f"  {score.name}: {score.score}")
```

### Historical Data Endpoints

#### `get_historical_odds(sport, date, **options)` → `HistoricalSnapshot`

Get historical odds data at a specific point in time.

```python
from datetime import datetime

# Get odds as they appeared on a specific date
snapshot = client.get_historical_odds(
    sport="americanfootball_nfl",
    date="2023-10-10T12:15:00Z",  # or datetime object
    regions=["us"],
    markets=["h2h", "spreads"]
)

print(f"Snapshot from: {snapshot.timestamp}")
print(f"Previous: {snapshot.previous_timestamp}")
print(f"Next: {snapshot.next_timestamp}")
print(f"Events: {len(snapshot.data)}")
```

#### `get_historical_events(sport, date, **options)` → `HistoricalSnapshot`

Get historical events data at a specific point in time.

```python
# Get events as they appeared historically
events_snapshot = client.get_historical_events(
    sport="americanfootball_nfl",
    date=datetime(2023, 10, 10, 12, 0, 0),
    commence_time_from="2023-10-10T00:00:00Z"
)
```

#### `get_historical_event_odds(sport, event_id, date, **options)` → `HistoricalSnapshot`

Get historical odds for a specific event including player props.

```python
# Get historical player prop odds
event_snapshot = client.get_historical_event_odds(
    sport="americanfootball_nfl",
    event_id="event-id-123",
    date="2023-10-10T12:15:00Z",
    regions=["us"],
    markets=["player_pass_tds", "alternate_spreads"]
)
```

## Data Models

All models now include optional enhanced fields:

```python
@dataclass(frozen=True)
class Outcome:
    name: str
    price: Union[float, int]
    point: Optional[float] = None          # For spreads/totals
    description: Optional[str] = None      # Additional outcome info
    link: Optional[str] = None             # Bookmaker betslip link
    sid: Optional[str] = None              # Bookmaker source ID
    bet_limit: Optional[float] = None      # Bet limit (exchanges)

@dataclass(frozen=True)
class Market:
    key: str
    outcomes: List[Outcome]
    last_update: Optional[datetime] = None
    link: Optional[str] = None             # Market link
    sid: Optional[str] = None              # Market source ID

@dataclass(frozen=True)
class Bookmaker:
    key: str
    title: str
    last_update: Optional[datetime]
    markets: List[Market]
    link: Optional[str] = None             # Event link
    sid: Optional[str] = None              # Event source ID

@dataclass(frozen=True)
class Event:
    id: str
    sport_key: str
    sport_title: str                       # Display name of sport
    commence_time: datetime
    home_team: Optional[str]
    away_team: Optional[str]
    bookmakers: List[Bookmaker]

@dataclass(frozen=True)
class HistoricalSnapshot:
    timestamp: datetime                    # Snapshot timestamp
    previous_timestamp: Optional[datetime] # Previous available snapshot
    next_timestamp: Optional[datetime]     # Next available snapshot
    data: Union[List[Event], List[EventWithoutOdds], Event]
```

## Advanced Examples

### Complete Odds Analysis with Enhanced Features

```python
def analyze_odds_with_links(sport_key: str):
    """Comprehensive odds analysis with bookmaker links."""
    
    # Get odds with all enhanced features
    odds = client.get_odds(
        sport_key,
        regions=["us"],
        markets=["h2h", "spreads", "totals"],
        include_links=True,
        include_sids=True,
        include_bet_limits=True
    )
    
    for event in odds:
        print(f"\n{event.away_team} @ {event.home_team}")
        print(f"Event ID: {event.id}")
        
        for bookmaker in event.bookmakers:
            print(f"\n  {bookmaker.title}")
            if bookmaker.link:
                print(f"    Event Link: {bookmaker.link}")
            
            for market in bookmaker.markets:
                print(f"    Market: {market.key}")
                if market.link:
                    print(f"      Market Link: {market.link}")
                
                for outcome in market.outcomes:
                    print(f"      {outcome.name}: {outcome.price}")
                    if outcome.link:
                        print(f"        Bet Link: {outcome.link}")
                    if outcome.bet_limit:
                        print(f"        Limit: ${outcome.bet_limit}")

# Usage
analyze_odds_with_links("americanfootball_nfl")
```

### Historical Odds Tracking

```python
def track_odds_movement(sport: str, event_id: str, hours_back: int = 24):
    """Track odds movement over time."""
    from datetime import datetime, timedelta
    
    snapshots = []
    current_time = datetime.now()
    
    # Get snapshots every hour for the past day
    for i in range(hours_back):
        snapshot_time = current_time - timedelta(hours=i)
        try:
            snapshot = client.get_historical_event_odds(
                sport=sport,
                event_id=event_id,
                date=snapshot_time,
                regions=["us"],
                markets=["h2h"]
            )
            snapshots.append(snapshot)
        except Exception:
            continue  # Snapshot might not exist
    
    # Analyze movement
    for snapshot in reversed(snapshots):
        print(f"\nTimestamp: {snapshot.timestamp}")
        if isinstance(snapshot.data, Event):
            event = snapshot.data
            for bookmaker in event.bookmakers:
                for market in bookmaker.markets:
                    if market.key == "h2h":
                        for outcome in market.outcomes:
                            print(f"  {outcome.name}: {outcome.price}")

# Usage
track_odds_movement("americanfootball_nfl", "event-id-123")
```

### Free Event Discovery

```python
def discover_upcoming_events():
    """Use the free events endpoint to discover upcoming games."""
    
    # Get sports first
    sports = client.get_sports()
    
    for sport in sports[:5]:  # Check first 5 sports
        try:
            events = client.get_events(sport.key)
            if events:
                print(f"\n{sport.title} ({len(events)} events):")
                for event in events[:3]:  # Show first 3 events
                    print(f"  {event.away_team} @ {event.home_team}")
                    print(f"    {event.commence_time}")
                    print(f"    ID: {event.id}")
        except Exception as e:
            print(f"Error getting {sport.title}: {e}")

# Usage (free - doesn't count against quota)
discover_upcoming_events()
```

## Authentication

```python
# Method 1: Direct initialization
client = OddsAPIClient(api_key="your-api-key")

# Method 2: Environment variable (recommended)
# Set ODDS_API_KEY=your-api-key
client = OddsAPIClient()

# Method 3: Context manager for automatic cleanup
with OddsAPIClient(api_key="your-api-key") as client:
    sports = client.get_sports()
```

## All Available Parameters

| Parameter | Type | Endpoints | Description |
|-----------|------|-----------|-------------|
| `all_sports` | `bool` | `get_sports` | Include inactive sports |
| `regions` | `List[Region]` | odds endpoints | `["us", "us2", "uk", "au", "eu", "us_dfs"]` |
| `markets` | `List[str]` | odds endpoints | `["h2h", "spreads", "totals", "outrights", ...]` |
| `odds_format` | `OddsFormat` | odds endpoints | `"decimal"` or `"american"` |
| `date_format` | `DateFormat` | all endpoints | `"iso"` or `"unix"` |
| `include_links` | `bool` | odds endpoints | Include bookmaker links |
| `include_sids` | `bool` | odds endpoints | Include source IDs |
| `include_bet_limits` | `bool` | odds endpoints | Include bet limits |
| `bookmakers` | `List[str]` | odds endpoints | Filter by bookmaker keys |
| `event_ids` | `List[str]` | multiple | Filter by event IDs |
| `commence_time_from` | `datetime\|str` | multiple | Start time filter |
| `commence_time_to` | `datetime\|str` | multiple | End time filter |
| `days_from` | `int` | `get_scores` | Include completed games |
| `date` | `datetime\|str` | historical | Historical snapshot date |

## Error Handling

```python
from the_odds_api_sdk import (
    OddsAPIError,
    OddsAPIAuthError,
    OddsAPINotFoundError,
    OddsAPIRateLimitError,
    OddsAPIServerError
)

try:
    odds = client.get_odds("americanfootball_nfl", regions=["us"])
except OddsAPIAuthError:
    print("Invalid API key")
except OddsAPIRateLimitError:
    print("Rate limit exceeded")
except OddsAPINotFoundError:
    print("Sport or event not found")
except OddsAPIServerError:
    print("API server error")
except OddsAPIError as e:
    print(f"General API error: {e}")
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- **SDK Repository**: [GitHub](https://github.com/ChristianJStarr/the-odds-api-sdk-python)
- [The Odds API Documentation](https://the-odds-api.com/liveapi/guides/v4/)
- [Supported Sports](https://the-odds-api.com/sports-odds-data/sports-apis.html)
- [Bookmaker Coverage](https://the-odds-api.com/sports-odds-data/bookmaker-apis.html)

## Tips

1. **Use Environment Variables**: Store your API key in `ODDS_API_KEY` environment variable
2. **Cache Results**: The API has rate limits, so cache responses when possible
3. **Filter Wisely**: Use specific regions and markets to reduce API usage
4. **Handle Timezones**: All times are in UTC by default
5. **Monitor Usage**: Check your API usage at [the-odds-api.com](https://the-odds-api.com)

---

## Disclaimer

This is an **unofficial** SDK and is not affiliated with, endorsed by, or connected to The Odds API or its official developers. 

This SDK is provided "as is" without warranty of any kind. Use at your own risk.

For official support, please contact [The Odds API](https://the-odds-api.com) directly.

---