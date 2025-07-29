"""
The main client for The Odds API SDK.
"""

import os
from datetime import datetime
from typing import List, Optional, Sequence, Union
from urllib.parse import urljoin

import requests

from .exceptions import (
    OddsAPIError,
    OddsAPIAuthError,
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


class OddsAPIClient:
    """
    Elegant Python client for The Odds API.
    
    This client provides a simple, intuitive interface to interact with The Odds API.
    All methods return strongly-typed data models for better IDE support and type safety.
    
    Examples:
        >>> client = OddsAPIClient(api_key="your-api-key")
        >>> sports = client.get_sports()
        >>> odds = client.get_odds("americanfootball_nfl", regions=["us"])
        >>> event_odds = client.get_event_odds("event-id", regions=["us"])
    """
    
    BASE_URL = "https://api.the-odds-api.com/v4/"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ) -> None:
        """
        Initialize the Odds API client.
        
        Args:
            api_key: Your Odds API key. If not provided, will look for ODDS_API_KEY env var.
            base_url: Base URL for the API. Defaults to official API URL.
            timeout: Request timeout in seconds. Defaults to 30.
            
        Raises:
            OddsAPIAuthError: If no API key is provided or found in environment.
        """
        self.api_key = api_key or os.getenv("ODDS_API_KEY")
        if not self.api_key:
            raise OddsAPIAuthError("API key is required. Provide it directly or set ODDS_API_KEY environment variable.")
        
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            "User-Agent": "the-odds-api-python-sdk/1.0.0",
            "Accept": "application/json",
        })
    
    def get_sports(self, *, all_sports: bool = False) -> List[Sport]:
        """
        Get all available sports.
        
        Args:
            all_sports: When True, returns all sports including inactive ones.
                       When False (default), only returns recently updated (in-season) sports.
        
        Returns:
            List of Sport objects representing available sports.
            
        Examples:
            >>> # Get only in-season sports
            >>> sports = client.get_sports()
            
            >>> # Get all sports including inactive ones
            >>> all_sports = client.get_sports(all_sports=True)
            >>> nfl_sport = next(s for s in all_sports if s.key == "americanfootball_nfl")
        """
        params = {"apiKey": self.api_key}
        if all_sports:
            params["all"] = "true"
        
        response = self._make_request("sports", params=params)
        return [self._parse_sport(sport_data) for sport_data in response]
    
    def get_odds(
        self,
        sport: str,
        *,
        regions: Optional[Sequence[Region]] = None,
        markets: Optional[Sequence[MarketType]] = None,
        odds_format: OddsFormat = "decimal",
        date_format: DateFormat = "iso",
        event_ids: Optional[Sequence[str]] = None,
        bookmakers: Optional[Sequence[str]] = None,
        commence_time_from: Optional[Union[str, datetime]] = None,
        commence_time_to: Optional[Union[str, datetime]] = None,
        include_links: bool = False,
        include_sids: bool = False,
        include_bet_limits: bool = False,
    ) -> List[Event]:
        """
        Get odds for a specific sport.
        
        Args:
            sport: Sport key (e.g., "americanfootball_nfl") or "upcoming" for all sports.
            regions: List of regions to include (e.g., ["us", "uk"]).
            markets: List of markets to include (e.g., ["h2h", "spreads"]).
            odds_format: Format for odds ("decimal" or "american").
            date_format: Format for dates ("iso" or "unix").
            event_ids: Filter by specific event IDs.
            bookmakers: Filter by specific bookmakers.
            commence_time_from: Filter events starting from this time.
            commence_time_to: Filter events ending before this time.
            include_links: Include bookmaker links to events, markets, and betslips.
            include_sids: Include source IDs (bookmaker IDs) for events, markets, and outcomes.
            include_bet_limits: Include bet limits for each betting option (mainly for exchanges).
            
        Returns:
            List of Event objects with odds from various bookmakers.
            
        Examples:
            >>> # Get NFL odds from US bookmakers
            >>> odds = client.get_odds("americanfootball_nfl", regions=["us"])
            
            >>> # Get upcoming games with spreads and totals, including links
            >>> odds = client.get_odds("upcoming", 
            ...                       regions=["us"], 
            ...                       markets=["spreads", "totals"],
            ...                       include_links=True)
        """
        params = self._build_odds_params(
            regions=regions,
            markets=markets,
            odds_format=odds_format,
            date_format=date_format,
            event_ids=event_ids,
            bookmakers=bookmakers,
            commence_time_from=commence_time_from,
            commence_time_to=commence_time_to,
            include_links=include_links,
            include_sids=include_sids,
            include_bet_limits=include_bet_limits,
        )
        
        response = self._make_request(f"sports/{sport}/odds", params=params)
        return [self._parse_event(event_data, date_format) for event_data in response]
    
    def get_event_odds(
        self,
        sport: str,
        event_id: str,
        *,
        regions: Optional[Sequence[Region]] = None,
        markets: Optional[Sequence[str]] = None,  # Allow any market type for events
        odds_format: OddsFormat = "decimal",
        date_format: DateFormat = "iso",
        include_links: bool = False,
        include_sids: bool = False,
        include_bet_limits: bool = False,
    ) -> Event:
        """
        Get odds for a specific event.
        
        This endpoint supports all available betting markets, including player props
        and other specialized markets not available in the main odds endpoint.
        
        Args:
            sport: Sport key (e.g., "americanfootball_nfl").
            event_id: The specific event ID.
            regions: List of regions to include.
            markets: List of markets to include (supports all market types).
            odds_format: Format for odds ("decimal" or "american").
            date_format: Format for dates ("iso" or "unix").
            include_links: Include bookmaker links to events, markets, and betslips.
            include_sids: Include source IDs (bookmaker IDs) for events, markets, and outcomes.
            include_bet_limits: Include bet limits for each betting option (mainly for exchanges).
            
        Returns:
            Event object with odds for the specified event.
            
        Examples:
            >>> # Get player prop odds for a specific game
            >>> event = client.get_event_odds("americanfootball_nfl", 
            ...                              "event-id-123",
            ...                              regions=["us"],
            ...                              markets=["player_pass_tds"],
            ...                              include_links=True)
        """
        params = self._build_odds_params(
            regions=regions,
            markets=markets,
            odds_format=odds_format,
            date_format=date_format,
            include_links=include_links,
            include_sids=include_sids,
            include_bet_limits=include_bet_limits,
        )
        
        response = self._make_request(f"sports/{sport}/events/{event_id}/odds", params=params)
        return self._parse_event(response, date_format)
    
    def get_events(
        self,
        sport: str,
        *,
        date_format: DateFormat = "iso",
        event_ids: Optional[Sequence[str]] = None,
        commence_time_from: Optional[Union[str, datetime]] = None,
        commence_time_to: Optional[Union[str, datetime]] = None,
    ) -> List[EventWithoutOdds]:
        """
        Get events without odds for a specific sport.
        
        This endpoint is free and does not count against your usage quota.
        Use it to get event IDs and basic event information.
        
        Args:
            sport: Sport key (e.g., "americanfootball_nfl").
            date_format: Format for dates ("iso" or "unix").
            event_ids: Filter by specific event IDs.
            commence_time_from: Filter events starting from this time.
            commence_time_to: Filter events ending before this time.
            
        Returns:
            List of EventWithoutOdds objects.
            
        Examples:
            >>> # Get all upcoming NFL events
            >>> events = client.get_events("americanfootball_nfl")
            
            >>> # Get events in a specific time range
            >>> from datetime import datetime, timedelta
            >>> tomorrow = datetime.now() + timedelta(days=1)
            >>> events = client.get_events("americanfootball_nfl", 
            ...                           commence_time_from=tomorrow)
        """
        params = self._build_events_params(
            date_format=date_format,
            event_ids=event_ids,
            commence_time_from=commence_time_from,
            commence_time_to=commence_time_to,
        )
        
        response = self._make_request(f"sports/{sport}/events", params=params)
        return [self._parse_event_without_odds(event_data, date_format) for event_data in response]
    
    def get_participants(self, sport: str) -> List[Participant]:
        """
        Get participants (teams or players) for a specific sport.
        
        Depending on the sport, a participant can be either a team or an individual.
        For example, for NBA this returns teams, for tennis it returns players.
        This endpoint does not return players on a team.
        
        Args:
            sport: Sport key (e.g., "americanfootball_nfl").
            
        Returns:
            List of Participant objects.
            
        Examples:
            >>> # Get all NFL teams
            >>> teams = client.get_participants("americanfootball_nfl")
            >>> chiefs = next(t for t in teams if "Chiefs" in t.full_name)
        """
        params = {"apiKey": self.api_key}
        response = self._make_request(f"sports/{sport}/participants", params=params)
        return [self._parse_participant(participant_data) for participant_data in response]
    
    def get_scores(
        self,
        sport: str,
        *,
        days_from: Optional[int] = None,
        date_format: DateFormat = "iso",
    ) -> List[EventScore]:
        """
        Get scores for live and completed games.
        
        Args:
            sport: Sport key (e.g., "americanfootball_nfl") or "upcoming" for all sports.
            days_from: Get completed games from this many days ago. If not specified,
                      only returns live and upcoming games.
            date_format: Format for dates ("iso" or "unix").
            
        Returns:
            List of EventScore objects with game scores.
            
        Note:
            - Without days_from: Returns live and upcoming games (quota cost: 1)
            - With days_from: Returns live, upcoming, and completed games (quota cost: 2)
            - Only live and completed games will have scores populated
            
        Examples:
            >>> # Get live and upcoming games only
            >>> scores = client.get_scores("americanfootball_nfl")
            
            >>> # Get games from last 3 days including completed
            >>> scores = client.get_scores("americanfootball_nfl", days_from=3)
        """
        params = {"apiKey": self.api_key}
        
        if days_from is not None:
            params["daysFrom"] = str(days_from)
        
        if date_format:
            params["dateFormat"] = date_format
        
        response = self._make_request(f"sports/{sport}/scores", params=params)
        return [self._parse_event_score(score_data, date_format) for score_data in response]
    
    def get_historical_odds(
        self,
        sport: str,
        date: Union[str, datetime],
        *,
        regions: Optional[Sequence[Region]] = None,
        markets: Optional[Sequence[MarketType]] = None,
        odds_format: OddsFormat = "decimal",
        date_format: DateFormat = "iso",
        event_ids: Optional[Sequence[str]] = None,
        bookmakers: Optional[Sequence[str]] = None,
    ) -> HistoricalSnapshot:
        """
        Get historical odds data for a specific sport at a point in time.
        
        This endpoint returns featured markets (h2h, spreads, totals, outrights) only.
        Historical snapshots are available from June 2020 at 10-minute intervals until
        Sep 2022, and at 5-minute intervals thereafter.
        
        Args:
            sport: Sport key (e.g., "americanfootball_nfl").
            date: The timestamp of the snapshot in ISO8601 format or datetime object.
            regions: List of regions to include.
            markets: List of markets to include (featured markets only).
            odds_format: Format for odds ("decimal" or "american").
            date_format: Format for dates ("iso" or "unix").
            event_ids: Filter by specific event IDs.
            bookmakers: Filter by specific bookmakers.
            
        Returns:
            HistoricalSnapshot object with timestamp info and event data.
            
        Examples:
            >>> # Get NFL odds as they were on a specific date
            >>> from datetime import datetime
            >>> snapshot = client.get_historical_odds(
            ...     "americanfootball_nfl",
            ...     "2023-10-10T12:15:00Z",
            ...     regions=["us"],
            ...     markets=["h2h", "spreads"]
            ... )
            >>> print(f"Snapshot from: {snapshot.timestamp}")
            >>> print(f"Previous snapshot: {snapshot.previous_timestamp}")
        """
        params = self._build_odds_params(
            regions=regions,
            markets=markets,
            odds_format=odds_format,
            date_format=date_format,
            event_ids=event_ids,
            bookmakers=bookmakers,
        )
        
        # Add date parameter
        if isinstance(date, datetime):
            params["date"] = date.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            params["date"] = date
        
        response = self._make_request(f"historical/sports/{sport}/odds", params=params)
        return self._parse_historical_snapshot(response, date_format, is_single_event=False)
    
    def get_historical_events(
        self,
        sport: str,
        date: Union[str, datetime],
        *,
        date_format: DateFormat = "iso",
        event_ids: Optional[Sequence[str]] = None,
        commence_time_from: Optional[Union[str, datetime]] = None,
        commence_time_to: Optional[Union[str, datetime]] = None,
    ) -> HistoricalSnapshot:
        """
        Get historical events data for a specific sport at a point in time.
        
        Returns events as they appeared at the specified timestamp, without odds.
        
        Args:
            sport: Sport key (e.g., "americanfootball_nfl").
            date: The timestamp of the snapshot in ISO8601 format or datetime object.
            date_format: Format for dates ("iso" or "unix").
            event_ids: Filter by specific event IDs.
            commence_time_from: Filter events starting from this time.
            commence_time_to: Filter events ending before this time.
            
        Returns:
            HistoricalSnapshot object with timestamp info and events data.
            
        Examples:
            >>> # Get events as they appeared on a specific date
            >>> snapshot = client.get_historical_events(
            ...     "americanfootball_nfl",
            ...     "2023-10-10T12:15:00Z"
            ... )
        """
        params = self._build_events_params(
            date_format=date_format,
            event_ids=event_ids,
            commence_time_from=commence_time_from,
            commence_time_to=commence_time_to,
        )
        
        # Add date parameter
        if isinstance(date, datetime):
            params["date"] = date.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            params["date"] = date
        
        response = self._make_request(f"historical/sports/{sport}/events", params=params)
        return self._parse_historical_snapshot(response, date_format, is_single_event=False, events_only=True)
    
    def get_historical_event_odds(
        self,
        sport: str,
        event_id: str,
        date: Union[str, datetime],
        *,
        regions: Optional[Sequence[Region]] = None,
        markets: Optional[Sequence[str]] = None,
        odds_format: OddsFormat = "decimal",
        date_format: DateFormat = "iso",
        bookmakers: Optional[Sequence[str]] = None,
    ) -> HistoricalSnapshot:
        """
        Get historical odds for a specific event at a point in time.
        
        This endpoint supports all available betting markets, including player props.
        Historical snapshots for non-featured markets are available from May 2023.
        
        Args:
            sport: Sport key (e.g., "americanfootball_nfl").
            event_id: The specific event ID.
            date: The timestamp of the snapshot in ISO8601 format or datetime object.
            regions: List of regions to include.
            markets: List of markets to include (supports all market types).
            odds_format: Format for odds ("decimal" or "american").
            date_format: Format for dates ("iso" or "unix").
            bookmakers: Filter by specific bookmakers.
            
        Returns:
            HistoricalSnapshot object with timestamp info and single event data.
            
        Examples:
            >>> # Get historical player prop odds for a specific game
            >>> snapshot = client.get_historical_event_odds(
            ...     "americanfootball_nfl",
            ...     "event-id-123",
            ...     "2023-10-10T12:15:00Z",
            ...     regions=["us"],
            ...     markets=["player_pass_tds"]
            ... )
        """
        params = self._build_odds_params(
            regions=regions,
            markets=markets,
            odds_format=odds_format,
            date_format=date_format,
            bookmakers=bookmakers,
        )
        
        # Add date parameter
        if isinstance(date, datetime):
            params["date"] = date.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            params["date"] = date
        
        response = self._make_request(f"historical/sports/{sport}/events/{event_id}/odds", params=params)
        return self._parse_historical_snapshot(response, date_format, is_single_event=True)
    
    def _build_odds_params(self, **kwargs) -> dict:
        """Build parameters for odds requests."""
        params = {"apiKey": self.api_key}
        
        # Handle list parameters
        if kwargs.get("regions"):
            params["regions"] = ",".join(kwargs["regions"])
        if kwargs.get("markets"):
            params["markets"] = ",".join(kwargs["markets"])
        if kwargs.get("event_ids"):
            params["eventIds"] = ",".join(kwargs["event_ids"])
        if kwargs.get("bookmakers"):
            params["bookmakers"] = ",".join(kwargs["bookmakers"])
        
        # Handle simple parameters
        for key in ["odds_format", "date_format"]:
            if kwargs.get(key):
                param_key = "oddsFormat" if key == "odds_format" else "dateFormat"
                params[param_key] = kwargs[key]
        
        # Handle boolean parameters
        for key in ["include_links", "include_sids", "include_bet_limits"]:
            if kwargs.get(key):
                param_key = key.replace("_", "").replace("include", "include")
                param_key = param_key[0].lower() + param_key[1:]  # camelCase
                if key == "include_links":
                    param_key = "includeLinks"
                elif key == "include_sids":
                    param_key = "includeSids"
                elif key == "include_bet_limits":
                    param_key = "includeBetLimits"
                params[param_key] = "true"
        
        # Handle datetime parameters
        for key in ["commence_time_from", "commence_time_to"]:
            if kwargs.get(key):
                value = kwargs[key]
                if isinstance(value, datetime):
                    # Format as required by the API: YYYY-MM-DDTHH:MM:SSZ
                    value = value.strftime("%Y-%m-%dT%H:%M:%SZ")
                param_key = "commenceTimeFrom" if key == "commence_time_from" else "commenceTimeTo"
                params[param_key] = value
        
        return {k: v for k, v in params.items() if v is not None}
    
    def _build_events_params(self, **kwargs) -> dict:
        """Build parameters for events requests."""
        params = {"apiKey": self.api_key}
        
        # Handle list parameters
        if kwargs.get("event_ids"):
            params["eventIds"] = ",".join(kwargs["event_ids"])
        
        # Handle simple parameters
        if kwargs.get("date_format"):
            params["dateFormat"] = kwargs["date_format"]
        
        # Handle datetime parameters
        for key in ["commence_time_from", "commence_time_to"]:
            if kwargs.get(key):
                value = kwargs[key]
                if isinstance(value, datetime):
                    value = value.strftime("%Y-%m-%dT%H:%M:%SZ")
                param_key = "commenceTimeFrom" if key == "commence_time_from" else "commenceTimeTo"
                params[param_key] = value
        
        return {k: v for k, v in params.items() if v is not None}
    
    def _make_request(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make a request to the API with proper error handling."""
        url = urljoin(self.base_url, endpoint)
        
        if params is None:
            params = {"apiKey": self.api_key}
        elif "apiKey" not in params:
            params["apiKey"] = self.api_key
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            self._handle_response_errors(response)
            return response.json()
        except ValueError as e:
            raise OddsAPIError(f"Failed to parse response: {str(e)}")
        except requests.exceptions.Timeout:
            raise OddsAPIError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise OddsAPIError("Failed to connect to the API")
        except requests.exceptions.RequestException as e:
            raise OddsAPIError(f"Request failed: {str(e)}")
    
    def _handle_response_errors(self, response: requests.Response) -> None:
        """Handle HTTP response errors with specific exception types."""
        if response.status_code == 200:
            return
        
        try:
            error_data = response.json()
            message = error_data.get("message", response.text)
        except ValueError:
            message = response.text or f"HTTP {response.status_code} error"
        
        if response.status_code == 401:
            if "usage limit" in message.lower():
                from .exceptions import OddsAPIUsageLimitError
                raise OddsAPIUsageLimitError(message)
            else:
                raise OddsAPIAuthError(message)
        elif response.status_code == 404:
            raise OddsAPINotFoundError(message)
        elif response.status_code == 422:
            from .exceptions import OddsAPIValidationError
            raise OddsAPIValidationError(message)
        elif response.status_code == 429:
            raise OddsAPIRateLimitError(message)
        elif response.status_code >= 500:
            raise OddsAPIServerError(message)
        else:
            raise OddsAPIError(message, response.status_code)
    
    def _parse_sport(self, data: dict) -> Sport:
        """Parse sport data into Sport object."""
        return Sport(
            key=data["key"],
            group=data["group"],
            title=data["title"],
            description=data["description"],
            active=data["active"],
            has_outrights=data["has_outrights"],
        )
    
    def _parse_event(self, data: dict, date_format: DateFormat) -> Event:
        """Parse event data into Event object."""
        commence_time = self._parse_datetime(data["commence_time"], date_format)
        
        bookmakers = []
        for bookmaker_data in data.get("bookmakers", []):
            bookmakers.append(self._parse_bookmaker(bookmaker_data, date_format))
        
        return Event(
            id=data["id"],
            sport_key=data["sport_key"],
            sport_title=data["sport_title"],
            commence_time=commence_time,
            home_team=data["home_team"],
            away_team=data["away_team"],
            bookmakers=bookmakers,
        )
    
    def _parse_event_without_odds(self, data: dict, date_format: DateFormat) -> EventWithoutOdds:
        """Parse event data into EventWithoutOdds object."""
        commence_time = self._parse_datetime(data["commence_time"], date_format)
        
        return EventWithoutOdds(
            id=data["id"],
            sport_key=data["sport_key"],
            sport_title=data["sport_title"],
            commence_time=commence_time,
            home_team=data["home_team"],
            away_team=data["away_team"],
        )
    
    def _parse_participant(self, data: dict) -> Participant:
        """Parse participant data into Participant object."""
        return Participant(
            id=data["id"],
            full_name=data["full_name"],
        )
    
    def _parse_historical_snapshot(
        self, 
        data: dict, 
        date_format: DateFormat, 
        is_single_event: bool = False,
        events_only: bool = False
    ) -> HistoricalSnapshot:
        """Parse historical snapshot data into HistoricalSnapshot object."""
        timestamp = self._parse_datetime(data["timestamp"], date_format)
        
        previous_timestamp = None
        if data.get("previous_timestamp"):
            previous_timestamp = self._parse_datetime(data["previous_timestamp"], date_format)
        
        next_timestamp = None
        if data.get("next_timestamp"):
            next_timestamp = self._parse_datetime(data["next_timestamp"], date_format)
        
        # Parse the data field
        if is_single_event:
            # Single event with odds
            parsed_data = self._parse_event(data["data"], date_format)
        elif events_only:
            # List of events without odds
            parsed_data = [self._parse_event_without_odds(event_data, date_format) for event_data in data["data"]]
        else:
            # List of events with odds
            parsed_data = [self._parse_event(event_data, date_format) for event_data in data["data"]]
        
        return HistoricalSnapshot(
            timestamp=timestamp,
            previous_timestamp=previous_timestamp,
            next_timestamp=next_timestamp,
            data=parsed_data,
        )
    
    def _parse_bookmaker(self, data: dict, date_format: DateFormat) -> Bookmaker:
        """Parse bookmaker data into Bookmaker object."""
        # Some bookmakers might not have last_update field
        last_update = None
        if "last_update" in data:
            last_update = self._parse_datetime(data["last_update"], date_format)
        
        markets = []
        for market_data in data.get("markets", []):
            markets.append(self._parse_market(market_data, date_format))
        
        return Bookmaker(
            key=data["key"],
            title=data["title"],
            last_update=last_update,
            markets=markets,
            link=data.get("link"),
            sid=data.get("sid"),
        )
    
    def _parse_market(self, data: dict, date_format: DateFormat) -> Market:
        """Parse market data into Market object."""
        outcomes = []
        for outcome_data in data.get("outcomes", []):
            outcomes.append(self._parse_outcome(outcome_data))
        
        last_update = None
        if "last_update" in data:
            last_update = self._parse_datetime(data["last_update"], date_format)
        
        return Market(
            key=data["key"],
            outcomes=outcomes,
            last_update=last_update,
            link=data.get("link"),
            sid=data.get("sid"),
        )
    
    def _parse_outcome(self, data: dict) -> Outcome:
        """Parse outcome data into Outcome object."""
        return Outcome(
            name=data["name"],
            price=data["price"],
            point=data.get("point"),
            description=data.get("description"),
            link=data.get("link"),
            sid=data.get("sid"),
            bet_limit=data.get("bet_limit"),
        )
    
    def _parse_event_score(self, data: dict, date_format: DateFormat) -> EventScore:
        """Parse event score data into EventScore object."""
        commence_time = self._parse_datetime(data["commence_time"], date_format)
        
        scores = None
        if data.get("scores"):
            scores = []
            for score_data in data["scores"]:
                scores.append(Score(
                    name=score_data["name"],
                    score=score_data.get("score")
                ))
        
        last_update = None
        if data.get("last_update"):
            last_update = self._parse_datetime(data["last_update"], date_format)
        
        return EventScore(
            id=data["id"],
            sport_key=data["sport_key"],
            sport_title=data["sport_title"],
            commence_time=commence_time,
            completed=data["completed"],
            home_team=data["home_team"],
            away_team=data["away_team"],
            scores=scores,
            last_update=last_update,
        )
    
    def _parse_datetime(self, timestamp: Union[str, int, float], date_format: DateFormat) -> datetime:
        """Parse timestamp into datetime object."""
        if date_format == "unix":
            return datetime.fromtimestamp(float(timestamp))
        else:
            # Handle ISO format
            timestamp_str = str(timestamp)
            if timestamp_str.endswith("Z"):
                timestamp_str = timestamp_str[:-1] + "+00:00"
            return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    
    def __enter__(self):
        """Support for context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support for context manager."""
        self.session.close() 