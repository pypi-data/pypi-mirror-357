"""
Unit tests for The Odds API client.
"""

import os
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from the_odds_api_sdk import OddsAPIClient, OddsAPIError, OddsAPIAuthError, OddsAPINotFoundError, Sport, Event, EventScore


class TestOddsAPIClient:
    """Test cases for OddsAPIClient."""
    
    def test_init_with_api_key(self):
        """Test client initialization with API key."""
        client = OddsAPIClient(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.base_url == "https://api.the-odds-api.com/v4/"
        assert client.timeout == 30
    
    def test_init_with_env_var(self):
        """Test client initialization with environment variable."""
        with patch.dict(os.environ, {"ODDS_API_KEY": "env-key"}):
            client = OddsAPIClient()
            assert client.api_key == "env-key"
    
    def test_init_without_api_key(self):
        """Test client initialization fails without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(OddsAPIAuthError):
                OddsAPIClient()
    
    def test_init_with_custom_params(self):
        """Test client initialization with custom parameters."""
        client = OddsAPIClient(
            api_key="test-key",
            base_url="https://custom.api.com/",
            timeout=60
        )
        assert client.base_url == "https://custom.api.com/"
        assert client.timeout == 60
    
    @patch('requests.Session.get')
    def test_get_sports_success(self, mock_get):
        """Test successful get_sports request."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "key": "americanfootball_nfl",
                "group": "American Football",
                "title": "NFL",
                "description": "US Football",
                "active": True,
                "has_outrights": False
            }
        ]
        mock_get.return_value = mock_response
        
        client = OddsAPIClient(api_key="test-key")
        sports = client.get_sports()
        
        assert len(sports) == 1
        assert isinstance(sports[0], Sport)
        assert sports[0].key == "americanfootball_nfl"
        assert sports[0].title == "NFL"
        assert sports[0].active is True
    
    @patch('requests.Session.get')
    def test_get_odds_success(self, mock_get):
        """Test successful get_odds request."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "test-event-id",
                "sport_key": "americanfootball_nfl",
                "sport_title": "NFL",
                "commence_time": "2023-12-01T20:00:00Z",
                "home_team": "Team A",
                "away_team": "Team B",
                "bookmakers": [
                    {
                        "key": "fanduel",
                        "title": "FanDuel",
                        "last_update": "2023-12-01T19:30:00Z",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": "Team A", "price": 1.5},
                                    {"name": "Team B", "price": 2.5}
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
        mock_get.return_value = mock_response
        
        client = OddsAPIClient(api_key="test-key")
        events = client.get_odds("americanfootball_nfl", regions=["us"])
        
        assert len(events) == 1
        assert isinstance(events[0], Event)
        assert events[0].id == "test-event-id"
        assert events[0].home_team == "Team A"
        assert len(events[0].bookmakers) == 1
        assert events[0].bookmakers[0].title == "FanDuel"
    
    @patch('requests.Session.get')
    def test_get_event_odds_success(self, mock_get):
        """Test successful get_event_odds request."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "test-event-id",
            "sport_key": "americanfootball_nfl",
            "sport_title": "NFL",
            "commence_time": "2023-12-01T20:00:00Z",
            "home_team": "Team A",
            "away_team": "Team B",
            "bookmakers": []
        }
        mock_get.return_value = mock_response
        
        client = OddsAPIClient(api_key="test-key")
        event = client.get_event_odds("americanfootball_nfl", "test-event-id")
        
        assert isinstance(event, Event)
        assert event.id == "test-event-id"
        assert event.home_team == "Team A"
    
    @patch('requests.Session.get')
    def test_auth_error(self, mock_get):
        """Test authentication error handling."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Invalid API key"}
        mock_get.return_value = mock_response
        
        client = OddsAPIClient(api_key="invalid-key")
        
        with pytest.raises(OddsAPIAuthError):
            client.get_sports()
    
    @patch('requests.Session.get')
    def test_not_found_error(self, mock_get):
        """Test not found error handling."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Sport not found"}
        mock_get.return_value = mock_response
        
        client = OddsAPIClient(api_key="test-key")
        
        with pytest.raises(OddsAPIError) as exc_info:
            client.get_odds("invalid_sport")
        
        assert exc_info.value.status_code == 404
    
    def test_build_odds_params(self):
        """Test parameter building for odds requests."""
        client = OddsAPIClient(api_key="test-key")
        
        params = client._build_odds_params(
            regions=["us", "uk"],
            markets=["h2h", "spreads"],
            odds_format="american",
            event_ids=["id1", "id2"]
        )
        
        assert params["regions"] == "us,uk"
        assert params["markets"] == "h2h,spreads"
        assert params["oddsFormat"] == "american"
        assert params["eventIds"] == "id1,id2"
        assert params["apiKey"] == "test-key"
    
    def test_build_odds_params_with_datetime(self):
        """Test parameter building with datetime objects."""
        client = OddsAPIClient(api_key="test-key")
        
        start_time = datetime(2023, 12, 1, 12, 0, 0)
        params = client._build_odds_params(
            commence_time_from=start_time,
            commence_time_to="2023-12-02T12:00:00Z"
        )
        
        assert params["commenceTimeFrom"] == "2023-12-01T12:00:00Z"
        assert params["commenceTimeTo"] == "2023-12-02T12:00:00Z"
    
    def test_parse_datetime_iso(self):
        """Test datetime parsing for ISO format."""
        client = OddsAPIClient(api_key="test-key")
        
        dt = client._parse_datetime("2023-12-01T20:00:00Z", "iso")
        assert isinstance(dt, datetime)
        assert dt.year == 2023
        assert dt.month == 12
        assert dt.day == 1
    
    def test_parse_datetime_unix(self):
        """Test datetime parsing for Unix format."""
        client = OddsAPIClient(api_key="test-key")
        
        dt = client._parse_datetime(1701453600, "unix")  # 2023-12-01 20:00:00 UTC
        assert isinstance(dt, datetime)
        assert dt.year == 2023
        assert dt.month == 12
        assert dt.day == 1
    
    def test_context_manager(self):
        """Test context manager functionality."""
        with patch.object(OddsAPIClient, '__init__', return_value=None):
            client = OddsAPIClient()
            client.session = Mock()
            
            with client as ctx_client:
                assert ctx_client is client
            
            client.session.close.assert_called_once()
    
    @patch('requests.Session.get')
    def test_connection_error(self, mock_get):
        """Test connection error handling."""
        from requests.exceptions import ConnectionError
        mock_get.side_effect = ConnectionError("Connection failed")
        
        client = OddsAPIClient(api_key="test-key")
        
        with pytest.raises(OddsAPIError) as exc_info:
            client.get_sports()
        
        assert "Failed to connect to the API" in str(exc_info.value)
    
    @patch('requests.Session.get')
    def test_timeout_error(self, mock_get):
        """Test timeout error handling."""
        from requests.exceptions import Timeout
        mock_get.side_effect = Timeout("Request timed out")
        
        client = OddsAPIClient(api_key="test-key")
        
        with pytest.raises(OddsAPIError) as exc_info:
            client.get_sports()
        
        assert "Request timed out" in str(exc_info.value)
    
    @patch('requests.Session.get')
    def test_get_scores_basic(self, mock_get):
        """Test basic get_scores functionality."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "test-event-1",
                "sport_key": "americanfootball_nfl",
                "sport_title": "NFL",
                "commence_time": "2024-01-15T20:00:00Z",
                "completed": False,
                "home_team": "Team A",
                "away_team": "Team B",
                "scores": None,
                "last_update": None
            }
        ]
        mock_get.return_value = mock_response
        
        client = OddsAPIClient(api_key="test-key")
        scores = client.get_scores("americanfootball_nfl")
        
        assert len(scores) == 1
        assert isinstance(scores[0], EventScore)
        assert scores[0].sport_title == "NFL"
        assert scores[0].completed is False
        assert scores[0].scores is None
        
        # Check API call
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "sports/americanfootball_nfl/scores" in args[0]
        assert kwargs['params']['apiKey'] == "test-key"
        assert 'daysFrom' not in kwargs['params']
    
    @patch('requests.Session.get')
    def test_get_scores_with_completed_games(self, mock_get):
        """Test get_scores with completed games and scores."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "completed-game",
                "sport_key": "americanfootball_nfl",
                "sport_title": "NFL", 
                "commence_time": "2024-01-15T20:00:00Z",
                "completed": True,
                "home_team": "Team A",
                "away_team": "Team B",
                "scores": [
                    {"name": "Team A", "score": "24"},
                    {"name": "Team B", "score": "17"}
                ],
                "last_update": "2024-01-15T23:30:00Z"
            }
        ]
        mock_get.return_value = mock_response
        
        client = OddsAPIClient(api_key="test-key")
        scores = client.get_scores("americanfootball_nfl", days_from=3)
        
        assert len(scores) == 1
        game = scores[0] 
        assert game.completed is True
        assert game.scores is not None
        assert len(game.scores) == 2
        assert game.scores[0].name == "Team A"
        assert game.scores[0].score == "24"
        assert game.last_update is not None
        
        # Check API call includes daysFrom parameter
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs['params']['daysFrom'] == '3'
    
    @patch('requests.Session.get')  
    def test_get_scores_error_handling(self, mock_get):
        """Test get_scores error handling."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Sport not found"}
        mock_get.return_value = mock_response
        
        client = OddsAPIClient(api_key="test-key")
        
        with pytest.raises(OddsAPINotFoundError):
            client.get_scores("invalid_sport")
    
    @patch('requests.Session.get')
    def test_get_events_success(self, mock_get):
        """Test successful get_events request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "test-event-id",
                "sport_key": "americanfootball_nfl",
                "sport_title": "NFL",
                "commence_time": "2023-12-01T20:00:00Z",
                "home_team": "Team A",
                "away_team": "Team B"
            }
        ]
        mock_get.return_value = mock_response
        
        client = OddsAPIClient(api_key="test-key")
        events = client.get_events("americanfootball_nfl")
        
        assert len(events) == 1
        from the_odds_api_sdk.models import EventWithoutOdds
        assert isinstance(events[0], EventWithoutOdds)
        assert events[0].id == "test-event-id"
        assert events[0].sport_title == "NFL"
        assert events[0].home_team == "Team A"
    
    @patch('requests.Session.get')
    def test_get_participants_success(self, mock_get):
        """Test successful get_participants request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "team-a-id",
                "full_name": "Team A Full Name"
            },
            {
                "id": "team-b-id", 
                "full_name": "Team B Full Name"
            }
        ]
        mock_get.return_value = mock_response
        
        client = OddsAPIClient(api_key="test-key")
        participants = client.get_participants("americanfootball_nfl")
        
        assert len(participants) == 2
        from the_odds_api_sdk.models import Participant
        assert isinstance(participants[0], Participant)
        assert participants[0].id == "team-a-id"
        assert participants[0].full_name == "Team A Full Name"
    
    @patch('requests.Session.get')
    def test_get_historical_odds_success(self, mock_get):
        """Test successful get_historical_odds request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "timestamp": "2023-12-01T12:00:00Z",
            "previous_timestamp": "2023-11-30T12:00:00Z",
            "next_timestamp": "2023-12-02T12:00:00Z",
            "data": [
                {
                    "id": "historical-event",
                    "sport_key": "americanfootball_nfl",
                    "sport_title": "NFL",
                    "commence_time": "2023-12-01T20:00:00Z",
                    "home_team": "Team A",
                    "away_team": "Team B",
                    "bookmakers": []
                }
            ]
        }
        mock_get.return_value = mock_response
        
        client = OddsAPIClient(api_key="test-key")
        snapshot = client.get_historical_odds("americanfootball_nfl", "2023-12-01")
        
        from the_odds_api_sdk.models import HistoricalSnapshot
        assert isinstance(snapshot, HistoricalSnapshot)
        assert snapshot.timestamp is not None
        assert snapshot.previous_timestamp is not None
        assert snapshot.next_timestamp is not None
        assert isinstance(snapshot.data, list)
        assert len(snapshot.data) == 1
    
    @patch('requests.Session.get')
    def test_get_historical_events_success(self, mock_get):
        """Test successful get_historical_events request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "timestamp": "2023-12-01T12:00:00Z",
            "previous_timestamp": None,
            "next_timestamp": "2023-12-02T12:00:00Z",
            "data": [
                {
                    "id": "historical-event",
                    "sport_key": "americanfootball_nfl",
                    "sport_title": "NFL",
                    "commence_time": "2023-12-01T20:00:00Z",
                    "home_team": "Team A",
                    "away_team": "Team B"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        client = OddsAPIClient(api_key="test-key")
        snapshot = client.get_historical_events("americanfootball_nfl", "2023-12-01")
        
        from the_odds_api_sdk.models import HistoricalSnapshot
        assert isinstance(snapshot, HistoricalSnapshot)
        assert snapshot.previous_timestamp is None
        assert len(snapshot.data) == 1
    
    @patch('requests.Session.get')
    def test_get_historical_event_odds_success(self, mock_get):
        """Test successful get_historical_event_odds request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "timestamp": "2023-12-01T12:00:00Z",
            "previous_timestamp": "2023-11-30T12:00:00Z",
            "next_timestamp": None,
            "data": {
                "id": "historical-event",
                "sport_key": "americanfootball_nfl",
                "sport_title": "NFL",
                "commence_time": "2023-12-01T20:00:00Z",
                "home_team": "Team A",
                "away_team": "Team B",
                "bookmakers": []
            }
        }
        mock_get.return_value = mock_response
        
        client = OddsAPIClient(api_key="test-key")
        snapshot = client.get_historical_event_odds(
            "americanfootball_nfl", "event-id", "2023-12-01"
        )
        
        from the_odds_api_sdk.models import HistoricalSnapshot
        assert isinstance(snapshot, HistoricalSnapshot)
        assert snapshot.next_timestamp is None
        assert hasattr(snapshot.data, 'id')  # It's an Event object, not a dict
    
    @patch('requests.Session.get')
    def test_rate_limit_error(self, mock_get):
        """Test rate limit error handling."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"message": "Rate limit exceeded"}
        mock_get.return_value = mock_response
        
        client = OddsAPIClient(api_key="test-key")
        
        from the_odds_api_sdk import OddsAPIRateLimitError
        with pytest.raises(OddsAPIRateLimitError):
            client.get_sports()
    
    @patch('requests.Session.get')
    def test_validation_error(self, mock_get):
        """Test validation error handling."""
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {"message": "Invalid parameters"}
        mock_get.return_value = mock_response
        
        client = OddsAPIClient(api_key="test-key")
        
        with pytest.raises(OddsAPIError) as exc_info:
            client.get_odds("americanfootball_nfl")
        
        assert exc_info.value.status_code == 422
    
    @patch('requests.Session.get')
    def test_server_error(self, mock_get):
        """Test server error handling."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal server error"}
        mock_get.return_value = mock_response
        
        client = OddsAPIClient(api_key="test-key")
        
        from the_odds_api_sdk import OddsAPIServerError
        with pytest.raises(OddsAPIServerError):
            client.get_sports()
    
    @patch('requests.Session.get')
    def test_usage_limit_error(self, mock_get):
        """Test usage limit error handling."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Usage limit exceeded"}
        mock_get.return_value = mock_response
        
        client = OddsAPIClient(api_key="test-key")
        
        from the_odds_api_sdk import OddsAPIUsageLimitError
        with pytest.raises(OddsAPIUsageLimitError):
            client.get_sports()
    
    def test_build_events_params(self):
        """Test parameter building for events requests."""
        client = OddsAPIClient(api_key="test-key")
        
        start_time = datetime(2023, 12, 1, 12, 0, 0)
        params = client._build_events_params(
            event_ids=["id1", "id2"],
            commence_time_from=start_time,
            commence_time_to="2023-12-02T12:00:00Z",
            date_format="unix"
        )
        
        assert params["eventIds"] == "id1,id2"
        assert params["commenceTimeFrom"] == "2023-12-01T12:00:00Z"
        assert params["commenceTimeTo"] == "2023-12-02T12:00:00Z"
        assert params["dateFormat"] == "unix"
        assert params["apiKey"] == "test-key"
    
    def test_parse_complex_odds_data(self):
        """Test parsing of complex odds data with all fields."""
        client = OddsAPIClient(api_key="test-key")
        
        event_data = {
            "id": "complex-event",
            "sport_key": "americanfootball_nfl",
            "sport_title": "NFL",
            "commence_time": "2023-12-01T20:00:00Z",
            "home_team": "Team A",
            "away_team": "Team B",
            "bookmakers": [
                {
                    "key": "fanduel",
                    "title": "FanDuel",
                    "last_update": "2023-12-01T19:30:00Z",
                    "link": "https://fanduel.com",
                    "sid": "fd-123",
                    "markets": [
                        {
                            "key": "h2h",
                            "last_update": "2023-12-01T19:30:00Z",
                            "link": "https://fanduel.com/h2h",
                            "sid": "fd-h2h-123",
                            "outcomes": [
                                {
                                    "name": "Team A",
                                    "price": 1.85,
                                    "point": None,
                                    "description": "Win",
                                    "link": "https://fanduel.com/bet",
                                    "sid": "fd-outcome-123",
                                    "bet_limit": 1000.0
                                },
                                {
                                    "name": "Team B",
                                    "price": 2.10,
                                    "point": None,
                                    "description": "Win"
                                }
                            ]
                        },
                        {
                            "key": "spreads",
                            "outcomes": [
                                {
                                    "name": "Team A",
                                    "price": 1.91,
                                    "point": -3.5
                                },
                                {
                                    "name": "Team B", 
                                    "price": 1.91,
                                    "point": 3.5
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        event = client._parse_event(event_data, "iso")
        
        assert event.id == "complex-event"
        assert len(event.bookmakers) == 1
        
        bookmaker = event.bookmakers[0]
        assert bookmaker.key == "fanduel"
        assert bookmaker.link == "https://fanduel.com"
        assert bookmaker.sid == "fd-123"
        assert len(bookmaker.markets) == 2
        
        h2h_market = bookmaker.markets[0]
        assert h2h_market.key == "h2h"
        assert h2h_market.link == "https://fanduel.com/h2h"
        assert h2h_market.sid == "fd-h2h-123"
        assert len(h2h_market.outcomes) == 2
        
        outcome = h2h_market.outcomes[0]
        assert outcome.name == "Team A"
        assert outcome.price == 1.85
        assert outcome.description == "Win"
        assert outcome.link == "https://fanduel.com/bet"
        assert outcome.sid == "fd-outcome-123"
        assert outcome.bet_limit == 1000.0
        
        spreads_market = bookmaker.markets[1]
        assert spreads_market.key == "spreads"
        assert spreads_market.outcomes[0].point == -3.5
        assert spreads_market.outcomes[1].point == 3.5
    
    def test_datetime_edge_cases(self):
        """Test datetime parsing edge cases."""
        client = OddsAPIClient(api_key="test-key")
        
        # Test Unix timestamp as string
        dt = client._parse_datetime("1701453600", "unix")
        assert dt.year == 2023
        
        # Test Unix timestamp as float
        dt = client._parse_datetime(1701453600.0, "unix")
        assert dt.year == 2023
        
        # Test ISO with microseconds
        dt = client._parse_datetime("2023-12-01T20:00:00.123456Z", "iso")
        assert dt.microsecond == 123456
    
    @patch('requests.Session.get')
    def test_json_decode_error(self, mock_get):
        """Test JSON decode error handling."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Invalid response"
        mock_get.return_value = mock_response
        
        client = OddsAPIClient(api_key="test-key")
        
        with pytest.raises(OddsAPIError) as exc_info:
            client.get_sports()
        
        assert "Failed to parse response" in str(exc_info.value)
    
    def test_get_odds_with_all_parameters(self):
        """Test get_odds with all possible parameters."""
        client = OddsAPIClient(api_key="test-key")
        
        start_time = datetime(2023, 12, 1, 12, 0, 0)
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = []
            
            client.get_odds(
                "americanfootball_nfl",
                regions=["us", "uk"],
                markets=["h2h", "spreads", "totals"],
                odds_format="american",
                date_format="unix",
                event_ids=["id1", "id2"],
                bookmakers=["fanduel", "draftkings"],
                commence_time_from=start_time,
                commence_time_to="2023-12-02T12:00:00Z",
                include_links=True,
                include_sids=True,
                include_bet_limits=True
            )
            
            # Verify the request was made with correct parameters
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            params = kwargs['params']
            
            assert params["regions"] == "us,uk"
            assert params["markets"] == "h2h,spreads,totals"
            assert params["oddsFormat"] == "american"
            assert params["dateFormat"] == "unix"
            assert params["eventIds"] == "id1,id2"
            assert params["bookmakers"] == "fanduel,draftkings"
            assert params["commenceTimeFrom"] == "2023-12-01T12:00:00Z"
            assert params["commenceTimeTo"] == "2023-12-02T12:00:00Z"
            assert params["includeLinks"] == "true"
            assert params["includeSids"] == "true"
            assert params["includeBetLimits"] == "true" 