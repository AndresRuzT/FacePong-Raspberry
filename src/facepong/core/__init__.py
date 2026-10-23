"""Core game engine logic and state representation."""

from facepong.core.ball import Ball
from facepong.core.game import Game, GameState
from facepong.core.paddle import Paddle
from facepong.core.score import ScoreManager

__all__ = ["Ball", "Game", "GameState", "Paddle", "ScoreManager"]
