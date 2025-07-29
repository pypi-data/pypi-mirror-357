"""
Unit tests for The Odds API data models.
"""

import pytest
from datetime import datetime
from the_odds_api_sdk.models import (
    Sport, Event, EventScore, EventWithoutOdds, Participant, 
    Bookmaker, Market, Outcome, Score, HistoricalSnapshot
)


class TestModels:
    """Test cases for data models."""
    
    def test_sport_creation(self):
        """Test Sport model creation."""
        sport = Sport(
            key="americanfootball_nfl",
            group="American Football",
            title="NFL",
            description="US Football",
            active=True,
            has_outrights=False
        )
        
        assert sport.key == "americanfootball_nfl"
        assert sport.group == "American Football"
        assert sport.title == "NFL"
        assert sport.description == "US Football"
        assert sport.active is True
        assert sport.has_outrights is False
    
    def test_outcome_creation_full(self):
        """Test Outcome model with all fields."""
        outcome = Outcome(
            name="Team A",
            price=1.85,
            point=-3.5,
            description="Spread bet",
            link="https://example.com/bet",
            sid="outcome-123",
            bet_limit=1000.0
        )
        
        assert outcome.name == "Team A"
        assert outcome.price == 1.85
        assert outcome.point == -3.5
        assert outcome.description == "Spread bet"
        assert outcome.link == "https://example.com/bet"
        assert outcome.sid == "outcome-123"
        assert outcome.bet_limit == 1000.0
    
    def test_outcome_creation_minimal(self):
        """Test Outcome model with minimal fields."""
        outcome = Outcome(
            name="Team B",
            price=2.10
        )
        
        assert outcome.name == "Team B"
        assert outcome.price == 2.10
        assert outcome.point is None
        assert outcome.description is None
        assert outcome.link is None
        assert outcome.sid is None
        assert outcome.bet_limit is None
    
    def test_market_creation(self):
        """Test Market model creation."""
        outcomes = [
            Outcome(name="Team A", price=1.85),
            Outcome(name="Team B", price=2.10)
        ]
        
        market = Market(
            key="h2h",
            outcomes=outcomes,
            last_update=datetime(2023, 12, 1, 19, 30),
            link="https://example.com/market",
            sid="market-123"
        )
        
        assert market.key == "h2h"
        assert len(market.outcomes) == 2
        assert market.outcomes[0].name == "Team A"
        assert market.last_update.year == 2023
        assert market.link == "https://example.com/market"
        assert market.sid == "market-123"
    
    def test_bookmaker_creation(self):
        """Test Bookmaker model creation."""
        outcomes = [Outcome(name="Team A", price=1.85)]
        markets = [Market(key="h2h", outcomes=outcomes)]
        
        bookmaker = Bookmaker(
            key="fanduel",
            title="FanDuel",
            last_update=datetime(2023, 12, 1, 19, 30),
            markets=markets,
            link="https://fanduel.com",
            sid="fd-123"
        )
        
        assert bookmaker.key == "fanduel"
        assert bookmaker.title == "FanDuel"
        assert len(bookmaker.markets) == 1
        assert bookmaker.markets[0].key == "h2h"
        assert bookmaker.link == "https://fanduel.com"
        assert bookmaker.sid == "fd-123"
    
    def test_event_creation(self):
        """Test Event model creation."""
        event = Event(
            id="event-123",
            sport_key="americanfootball_nfl",
            sport_title="NFL",
            commence_time=datetime(2023, 12, 1, 20, 0),
            home_team="Team A",
            away_team="Team B",
            bookmakers=[]
        )
        
        assert event.id == "event-123"
        assert event.sport_key == "americanfootball_nfl"
        assert event.sport_title == "NFL"
        assert event.commence_time.hour == 20
        assert event.home_team == "Team A"
        assert event.away_team == "Team B"
        assert len(event.bookmakers) == 0
    
    def test_event_without_odds_creation(self):
        """Test EventWithoutOdds model creation."""
        event = EventWithoutOdds(
            id="event-123",
            sport_key="americanfootball_nfl", 
            sport_title="NFL",
            commence_time=datetime(2023, 12, 1, 20, 0),
            home_team="Team A",
            away_team="Team B"
        )
        
        assert event.id == "event-123"
        assert event.sport_key == "americanfootball_nfl"
        assert event.sport_title == "NFL"
        assert event.commence_time.hour == 20
        assert event.home_team == "Team A"
        assert event.away_team == "Team B"
    
    def test_score_creation(self):
        """Test Score model creation."""
        score = Score(
            name="Team A",
            score="24"
        )
        
        assert score.name == "Team A"
        assert score.score == "24"
        
        # Test with integer score
        score_int = Score(
            name="Team B",
            score=17
        )
        
        assert score_int.name == "Team B"
        assert score_int.score == 17
        
        # Test with None score
        score_none = Score(name="Team C")
        assert score_none.name == "Team C"
        assert score_none.score is None
    
    def test_event_score_creation(self):
        """Test EventScore model creation."""
        scores = [
            Score(name="Team A", score="24"),
            Score(name="Team B", score="17")
        ]
        
        event_score = EventScore(
            id="event-123",
            sport_key="americanfootball_nfl",
            sport_title="NFL",
            commence_time=datetime(2023, 12, 1, 20, 0),
            completed=True,
            home_team="Team A",
            away_team="Team B",
            scores=scores,
            last_update=datetime(2023, 12, 1, 23, 30)
        )
        
        assert event_score.id == "event-123"
        assert event_score.sport_key == "americanfootball_nfl"
        assert event_score.sport_title == "NFL"
        assert event_score.completed is True
        assert event_score.home_team == "Team A"
        assert event_score.away_team == "Team B"
        assert len(event_score.scores) == 2
        assert event_score.scores[0].score == "24"
        assert event_score.last_update.hour == 23
    
    def test_participant_creation(self):
        """Test Participant model creation."""
        participant = Participant(
            id="team-123",
            full_name="Team Full Name"
        )
        
        assert participant.id == "team-123"
        assert participant.full_name == "Team Full Name"
    
    def test_historical_snapshot_creation_with_events_list(self):
        """Test HistoricalSnapshot with list of events."""
        events = [
            Event(
                id="event-1",
                sport_key="americanfootball_nfl",
                sport_title="NFL",
                commence_time=datetime(2023, 12, 1, 20, 0),
                home_team="Team A",
                away_team="Team B",
                bookmakers=[]
            ),
            Event(
                id="event-2",
                sport_key="americanfootball_nfl",
                sport_title="NFL",
                commence_time=datetime(2023, 12, 2, 20, 0),
                home_team="Team C",
                away_team="Team D",
                bookmakers=[]
            )
        ]
        
        snapshot = HistoricalSnapshot(
            timestamp=datetime(2023, 12, 1, 12, 0),
            previous_timestamp=datetime(2023, 11, 30, 12, 0),
            next_timestamp=datetime(2023, 12, 2, 12, 0),
            data=events
        )
        
        assert snapshot.timestamp.day == 1
        assert snapshot.previous_timestamp.day == 30
        assert snapshot.next_timestamp.day == 2
        assert isinstance(snapshot.data, list)
        assert len(snapshot.data) == 2
        assert snapshot.data[0].id == "event-1"
    
    def test_historical_snapshot_creation_with_single_event(self):
        """Test HistoricalSnapshot with single event."""
        event = Event(
            id="event-1",
            sport_key="americanfootball_nfl",
            sport_title="NFL",
            commence_time=datetime(2023, 12, 1, 20, 0),
            home_team="Team A",
            away_team="Team B",
            bookmakers=[]
        )
        
        snapshot = HistoricalSnapshot(
            timestamp=datetime(2023, 12, 1, 12, 0),
            previous_timestamp=None,
            next_timestamp=None,
            data=event
        )
        
        assert snapshot.timestamp.day == 1
        assert snapshot.previous_timestamp is None
        assert snapshot.next_timestamp is None
        assert isinstance(snapshot.data, Event)
        assert snapshot.data.id == "event-1"
    
    def test_frozen_dataclasses(self):
        """Test that dataclasses are frozen (immutable)."""
        sport = Sport(
            key="test",
            group="Test",
            title="Test Sport",
            description="Test Description",
            active=True,
            has_outrights=False
        )
        
        # Should not be able to modify frozen dataclass
        with pytest.raises(AttributeError):
            sport.key = "modified"
        
        # Test other models are also frozen
        outcome = Outcome(name="Test", price=1.5)
        with pytest.raises(AttributeError):
            outcome.price = 2.0
    
    def test_outcome_price_types(self):
        """Test Outcome accepts both int and float prices."""
        # Test with float
        outcome_float = Outcome(name="Team A", price=1.85)
        assert outcome_float.price == 1.85
        
        # Test with int  
        outcome_int = Outcome(name="Team B", price=2)
        assert outcome_int.price == 2
        
        # Test with negative (for American odds)
        outcome_negative = Outcome(name="Team C", price=-150)
        assert outcome_negative.price == -150 