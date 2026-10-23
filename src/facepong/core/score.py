"""Score tracking and victory evaluation."""

from __future__ import annotations


class ScoreManager:
    """Manages player scores, round progression and victory conditions."""

    def __init__(self, winning_score: int = 5) -> None:
        """Initialize score manager.

        Args:
            winning_score: Number of points required to win the match.
        """
        if winning_score < 1:
            raise ValueError(f"winning_score must be at least 1, got {winning_score}")
        self.winning_score = int(winning_score)
        self.p1_score = 0
        self.p2_score = 0
        self.winner: int | None = None

    @property
    def is_game_over(self) -> bool:
        """Check if any player has reached the winning score."""
        return self.winner is not None

    def add_point(self, player: int) -> bool:
        """Award a point to the designated player.

        Args:
            player: 1 for Player 1, 2 for Player 2.

        Returns:
            True if this point triggered match victory, False otherwise.
        """
        if self.is_game_over:
            return True

        if player == 1:
            self.p1_score += 1
            if self.p1_score >= self.winning_score:
                self.winner = 1
                return True
        elif player == 2:
            self.p2_score += 1
            if self.p2_score >= self.winning_score:
                self.winner = 2
                return True
        else:
            raise ValueError(f"Player must be 1 or 2, got {player}")

        return False

    def reset(self) -> None:
        """Reset scores and clear winner status."""
        self.p1_score = 0
        self.p2_score = 0
        self.winner = None
