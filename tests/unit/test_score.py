"""Tests for ScoreManager and match progression."""

import pytest

from facepong.core.score import ScoreManager


def test_score_initialization() -> None:
    """Verify initial score state."""
    sm = ScoreManager(winning_score=5)
    assert sm.p1_score == 0
    assert sm.p2_score == 0
    assert sm.winning_score == 5
    assert not sm.is_game_over
    assert sm.winner is None


def test_score_invalid_limit() -> None:
    """Ensure non-positive winning score raises ValueError."""
    with pytest.raises(ValueError):
        ScoreManager(winning_score=0)


def test_score_progression_and_victory() -> None:
    """Test score accumulation up to victory threshold."""
    sm = ScoreManager(winning_score=3)

    assert not sm.add_point(1)
    assert sm.p1_score == 1
    assert not sm.is_game_over

    assert not sm.add_point(2)
    assert sm.p2_score == 1

    assert not sm.add_point(1)
    assert sm.p1_score == 2

    # Winning point for Player 1
    won = sm.add_point(1)
    assert won is True
    assert sm.is_game_over
    assert sm.winner == 1

    # Further points are ignored once game is over
    sm.add_point(2)
    assert sm.p2_score == 1


def test_score_reset() -> None:
    """Verify score reset clears counters and winner."""
    sm = ScoreManager(winning_score=3)
    sm.add_point(1)
    sm.add_point(1)
    sm.add_point(1)
    assert sm.is_game_over

    sm.reset()
    assert sm.p1_score == 0
    assert sm.p2_score == 0
    assert sm.winner is None
    assert not sm.is_game_over
